
"""InVEST Crop Production Percentile Model."""
import collections
import logging
import os
import re

import numpy
import pygeoprocessing
import taskgraph
from osgeo import gdal
from osgeo import osr

from . import gettext
from . import spec
from . import utils
from . import validation
from .crop_production_regression import NUTRIENTS
from .unit_registry import u

LOGGER = logging.getLogger(__name__)

CROP_OPTIONS = {
    # Human-readable/translatable crop names come from three sources:
    # (1) Monfreda et. al. Table 1
    # (2) "EarthStat and FAO crop names and crop groups" table
    # (3) FAO's _World Programme for the Census of Agriculture 2020_
    # Where (1) and (2) differ, default to (1), except where (2) is
    # more descriptive (i.e., include additional list items, alternate
    # names, qualifiers, and other disambiguations).
    # Where discrepancies remain, consult (3) for additional context.
    # See #614 for more details and links to sources.
    "abaca": {"description": gettext("Abaca (manila hemp)")},
    "agave": {"description": gettext("Agave fibers, other")},
    "alfalfa": {"description": gettext("Alfalfa")},
    "almond": {"description": gettext("Almonds, with shell")},
    "aniseetc": {"description": gettext("Anise, badian, fennel, coriander")},
    "apple": {"description": gettext("Apples")},
    "apricot": {"description": gettext("Apricots")},
    "areca": {"description": gettext("Areca nuts (betel)")},
    "artichoke": {"description": gettext("Artichokes")},
    "asparagus": {"description": gettext("Asparagus")},
    "avocado": {"description": gettext("Avocados")},
    "bambara": {"description": gettext("Bambara beans")},
    "banana": {"description": gettext("Bananas")},
    "barley": {"description": gettext("Barley")},
    "bean": {"description": gettext("Beans, dry")},
    "beetfor": {"description": gettext("Beets for fodder")},
    "berrynes": {"description": gettext("Berries, other")},
    "blueberry": {"description": gettext("Blueberries")},
    "brazil": {"description": gettext("Brazil nuts, with shell")},
    "broadbean": {"description": gettext("Broad beans, horse beans, dry")},
    "buckwheat": {"description": gettext("Buckwheat")},
    "cabbage": {"description": gettext("Cabbages and other brassicas")},
    "cabbagefor": {"description": gettext("Cabbage for fodder")},
    "canaryseed": {"description": gettext("Canary seed")},
    "carob": {"description": gettext("Carobs")},
    "carrot": {"description": gettext("Carrots and turnips")},
    "carrotfor": {"description": gettext("Carrots for fodder")},
    "cashew": {"description": gettext("Cashew nuts, with shell")},
    "cashewapple": {"description": gettext("Cashew apple")},
    "cassava": {"description": gettext("Cassava")},
    "castor": {"description": gettext("Castor beans")},
    "cauliflower": {"description": gettext("Cauliflower and broccoli")},
    "cerealnes": {"description": gettext("Cereals, other")},
    "cherry": {"description": gettext("Cherries")},
    "chestnut": {"description": gettext("Chestnuts")},
    "chickpea": {"description": gettext("Chick peas")},
    "chicory": {"description": gettext("Chicory roots")},
    "chilleetc": {"description": gettext("Chilies and peppers, green")},
    "cinnamon": {"description": gettext("Cinnamon (canella)")},
    "citrusnes": {"description": gettext("Citrus fruit, other")},
    "clove": {"description": gettext("Cloves")},
    "clover": {"description": gettext("Clover")},
    "cocoa": {"description": gettext("Cocoa beans")},
    "coconut": {"description": gettext("Coconuts")},
    "coffee": {"description": gettext("Coffee, green")},
    "cotton": {"description": gettext("Cotton")},
    "cowpea": {"description": gettext("Cow peas, dry")},
    "cranberry": {"description": gettext("Cranberries")},
    "cucumberetc": {"description": gettext("Cucumbers and gherkins")},
    "currant": {"description": gettext("Currants")},
    "date": {"description": gettext("Dates")},
    "eggplant": {"description": gettext("Eggplants (aubergines)")},
    "fibrenes": {"description": gettext("Fiber crops, other")},
    "fig": {"description": gettext("Figs")},
    "flax": {"description": gettext("Flax fiber and tow")},
    "fonio": {"description": gettext("Fonio")},
    "fornes": {"description": gettext("Forage products, other")},
    "fruitnes": {"description": gettext("Fresh fruit, other")},
    "garlic": {"description": gettext("Garlic")},
    "ginger": {"description": gettext("Ginger")},
    "gooseberry": {"description": gettext("Gooseberries")},
    "grape": {"description": gettext("Grapes")},
    "grapefruitetc": {"description": gettext("Grapefruit and pomelos")},
    "grassnes": {"description": gettext("Grasses, other")},
    "greenbean": {"description": gettext("Beans, green")},
    "greenbroadbean": {"description": gettext("Broad beans, green")},
    "greencorn": {"description": gettext("Green corn (maize)")},
    "greenonion": {"description": gettext("Onions and shallots, green")},
    "greenpea": {"description": gettext("Peas, green")},
    "groundnut": {"description": gettext("Groundnuts, with shell")},
    "hazelnut": {"description": gettext("Hazelnuts (filberts), with shell")},
    "hemp": {"description": gettext("Hemp fiber and tow")},
    "hempseed": {"description": gettext("Hempseed")},
    "hop": {"description": gettext("Hops")},
    "jute": {"description": gettext("Jute")},
    "jutelikefiber": {"description": gettext("Jute-like fibers")},
    "kapokfiber": {"description": gettext("Kapok fiber")},
    "kapokseed": {"description": gettext("Kapok seed in shell")},
    "karite": {"description": gettext("Karite nuts (shea nuts)")},
    "kiwi": {"description": gettext("Kiwi fruit")},
    "kolanut": {"description": gettext("Kola nuts")},
    "legumenes": {"description": gettext("Legumes, other")},
    "lemonlime": {"description": gettext("Lemons and limes")},
    "lentil": {"description": gettext("Lentils")},
    "lettuce": {"description": gettext("Lettuce and chicory")},
    "linseed": {"description": gettext("Linseed")},
    "lupin": {"description": gettext("Lupins")},
    "maize": {"description": gettext("Maize")},
    "maizefor": {"description": gettext("Maize for forage and silage")},
    "mango": {"description": gettext("Mangoes, mangosteens, guavas")},
    "mate": {"description": gettext("Mate")},
    "melonetc": {"description": gettext("Cantaloupes and other melons")},
    "melonseed": {"description": gettext("Melon seed")},
    "millet": {"description": gettext("Millet")},
    "mixedgrain": {"description": gettext("Mixed grain")},
    "mixedgrass": {"description": gettext("Mixed grasses and legumes")},
    "mushroom": {"description": gettext("Mushrooms and truffles")},
    "mustard": {"description": gettext("Mustard seed")},
    "nutmeg": {"description": gettext("Nutmeg, mace, and cardamoms")},
    "nutnes": {"description": gettext("Nuts, other")},
    "oats": {"description": gettext("Oats")},
    "oilpalm": {"description": gettext("Oil palm fruit")},
    "oilseedfor": {"description": gettext("Green oilseeds for fodder")},
    "oilseednes": {"description": gettext("Oilseeds, other")},
    "okra": {"description": gettext("Okra")},
    "olive": {"description": gettext("Olives")},
    "onion": {"description": gettext("Onions, dry")},
    "orange": {"description": gettext("Oranges")},
    "papaya": {"description": gettext("Papayas")},
    "pea": {"description": gettext("Peas, dry")},
    "peachetc": {"description": gettext("Peaches and nectarines")},
    "pear": {"description": gettext("Pears")},
    "pepper": {"description": gettext("Pepper (Piper spp.)")},
    "peppermint": {"description": gettext("Peppermint")},
    "persimmon": {"description": gettext("Persimmons")},
    "pigeonpea": {"description": gettext("Pigeon peas")},
    "pimento": {"description": gettext("Chilies and peppers, dry")},
    "pineapple": {"description": gettext("Pineapples")},
    "pistachio": {"description": gettext("Pistachios")},
    "plantain": {"description": gettext("Plantains")},
    "plum": {"description": gettext("Plums and sloes")},
    "poppy": {"description": gettext("Poppy seed")},
    "potato": {"description": gettext("Potatoes")},
    "pulsenes": {"description": gettext("Pulses, other")},
    "pumpkinetc": {"description": gettext("Pumpkins, squash, gourds")},
    "pyrethrum": {"description": gettext("Pyrethrum, dried flowers")},
    "quince": {"description": gettext("Quinces")},
    "quinoa": {"description": gettext("Quinoa")},
    "ramie": {"description": gettext("Ramie")},
    "rapeseed": {"description": gettext("Rapeseed")},
    "rasberry": {"description": gettext("Raspberries")},
    "rice": {"description": gettext("Rice")},
    "rootnes": {"description": gettext("Roots and tubers, other")},
    "rubber": {"description": gettext("Natural rubber")},
    "rye": {"description": gettext("Rye")},
    "ryefor": {"description": gettext("Rye grass for forage and silage")},
    "safflower": {"description": gettext("Safflower seed")},
    "sesame": {"description": gettext("Sesame seed")},
    "sisal": {"description": gettext("Sisal")},
    "sorghum": {"description": gettext("Sorghum")},
    "sorghumfor": {"description": gettext("Sorghum for forage and silage")},
    "sourcherry": {"description": gettext("Sour cherries")},
    "soybean": {"description": gettext("Soybeans")},
    "spicenes": {"description": gettext("Spices, other")},
    "spinach": {"description": gettext("Spinach")},
    "stonefruitnes": {"description": gettext("Stone fruit, other")},
    "strawberry": {"description": gettext("Strawberries")},
    "stringbean": {"description": gettext("String beans")},
    "sugarbeet": {"description": gettext("Sugar beets")},
    "sugarcane": {"description": gettext("Sugar cane")},
    "sugarnes": {"description": gettext("Sugar crops, other")},
    "sunflower": {"description": gettext("Sunflower seed")},
    "swedefor": {"description": gettext("Swedes for fodder")},
    "sweetpotato": {"description": gettext("Sweet potatoes")},
    "tangetc": {"description": gettext("Tangerines, mandarins, clementines")},
    "taro": {"description": gettext("Taro")},
    "tea": {"description": gettext("Tea")},
    "tobacco": {"description": gettext("Tobacco leaves")},
    "tomato": {"description": gettext("Tomatoes")},
    "triticale": {"description": gettext("Triticale")},
    "tropicalnes": {"description": gettext("Fresh tropical fruit, other")},
    "tung": {"description": gettext("Tung nuts")},
    "turnipfor": {"description": gettext("Turnips for fodder")},
    "vanilla": {"description": gettext("Vanilla")},
    "vegetablenes": {"description": gettext("Fresh vegetables, other")},
    "vegfor": {"description": gettext("Vegetables and roots for fodder")},
    "vetch": {"description": gettext("Vetches")},
    "walnut": {"description": gettext("Walnuts, with shell")},
    "watermelon": {"description": gettext("Watermelons")},
    "wheat": {"description": gettext("Wheat")},
    "yam": {"description": gettext("Yams")},
    "yautia": {"description": gettext("Yautia")},
}

nutrient_units = {
    "protein":     u.gram/u.hectogram,
    "lipid":       u.gram/u.hectogram,       # total lipid
    "energy":      u.kilojoule/u.hectogram,
    "ca":          u.milligram/u.hectogram,  # calcium
    "fe":          u.milligram/u.hectogram,  # iron
    "mg":          u.milligram/u.hectogram,  # magnesium
    "ph":          u.milligram/u.hectogram,  # phosphorus
    "k":           u.milligram/u.hectogram,  # potassium
    "na":          u.milligram/u.hectogram,  # sodium
    "zn":          u.milligram/u.hectogram,  # zinc
    "cu":          u.milligram/u.hectogram,  # copper
    "fl":          u.microgram/u.hectogram,  # fluoride
    "mn":          u.milligram/u.hectogram,  # manganese
    "se":          u.microgram/u.hectogram,  # selenium
    "vita":        u.IU/u.hectogram,         # vitamin A
    "betac":       u.microgram/u.hectogram,  # beta carotene
    "alphac":      u.microgram/u.hectogram,  # alpha carotene
    "vite":        u.milligram/u.hectogram,  # vitamin e
    "crypto":      u.microgram/u.hectogram,  # cryptoxanthin
    "lycopene":    u.microgram/u.hectogram,  # lycopene
    "lutein":      u.microgram/u.hectogram,  # lutein + zeaxanthin
    "betat":       u.milligram/u.hectogram,  # beta tocopherol
    "gammat":      u.milligram/u.hectogram,  # gamma tocopherol
    "deltat":      u.milligram/u.hectogram,  # delta tocopherol
    "vitc":        u.milligram/u.hectogram,  # vitamin C
    "thiamin":     u.milligram/u.hectogram,
    "riboflavin":  u.milligram/u.hectogram,
    "niacin":      u.milligram/u.hectogram,
    "pantothenic": u.milligram/u.hectogram,  # pantothenic acid
    "vitb6":       u.milligram/u.hectogram,  # vitamin B6
    "folate":      u.microgram/u.hectogram,
    "vitb12":      u.microgram/u.hectogram,  # vitamin B12
    "vitk":        u.microgram/u.hectogram,  # vitamin K
}

MODEL_SPEC = spec.build_model_spec({
    "model_id": "crop_production_percentile",
    "model_title": gettext("Crop Production: Percentile"),
    "userguide": "crop_production.html",
    "aliases": ("cpp",),
    "ui_spec": {
        "order": [
            ['workspace_dir', 'results_suffix'],
            ['model_data_path', 'landcover_raster_path', 'landcover_to_crop_table_path', 'aggregate_polygon_path']
        ]
    },
    "args_with_spatial_overlap": {
        "spatial_keys": [
            "landcover_raster_path",
            "aggregate_polygon_path",
        ],
        "different_projections_ok": True,
    },
    "args": {
        "workspace_dir": spec.WORKSPACE,
        "results_suffix": spec.SUFFIX,
        "n_workers": spec.N_WORKERS,
        "landcover_raster_path": {
            **spec.LULC,
            "projected": True,
            "projection_units": u.meter
        },
        "landcover_to_crop_table_path": {
            "type": "csv",
            "index_col": "crop_name",
            "columns": {
                "lucode": {"type": "integer"},
                "crop_name": {
                    "type": "option_string",
                    "options": CROP_OPTIONS
                }
            },
            "about": gettext(
                "A table that maps each LULC code from the LULC map to one of "
                "the 175 canonical crop names representing the crop grown in "
                "that LULC class."),
            "name": gettext("LULC to Crop Table")
        },
        "aggregate_polygon_path": {
            **spec.AOI,
            "projected": True,
            "required": False
        },
        "model_data_path": {
            "type": "directory",
            "contents": {
                "climate_percentile_yield_tables": {
                    "type": "directory",
                    "about": gettext(
                        "Table mapping each climate bin to yield percentiles "
                        "for each crop."),
                    "contents": {
                        "[CROP]_percentile_yield_table.csv": {
                            "type": "csv",
                            "index_col": "climate_bin",
                            "columns": {
                                "climate_bin": {"type": "integer"},
                                "yield_25th": {
                                    "type": "number",
                                    "units": u.metric_ton/u.hectare
                                },
                                "yield_50th": {
                                    "type": "number",
                                    "units": u.metric_ton/u.hectare
                                },
                                "yield_75th": {
                                    "type": "number",
                                    "units": u.metric_ton/u.hectare
                                },
                                "yield_95th": {
                                    "type": "number",
                                    "units": u.metric_ton/u.hectare
                                }
                            }
                        },
                    }
                },
                "extended_climate_bin_maps": {
                    "type": "directory",
                    "about": gettext("Maps of climate bins for each crop."),
                    "contents": {
                        "extendedclimatebins[CROP]": {
                            "type": "raster",
                            "bands": {1: {"type": "integer"}},
                        }
                    }
                },
                "observed_yield": {
                    "type": "directory",
                    "about": gettext("Maps of actual observed yield for each crop."),
                    "contents": {
                        "[CROP]_observed_yield.tif": {
                            "type": "raster",
                            "bands": {1: {
                                "type": "number",
                                "units": u.metric_ton/u.hectare
                            }}
                        }
                    }
                },
                "crop_nutrient.csv": {
                    "type": "csv",
                    "index_col": "crop",
                    "columns": {
                        "crop": {
                            "type": "option_string",
                            "options": CROP_OPTIONS
                        },
                        "percentrefuse": {
                            "type": "percent"
                        },
                        **{nutrient: {
                            "type": "number",
                            "units": units
                        } for nutrient, units in nutrient_units.items()}
                    }
                }
            },
            "about": gettext("Path to the InVEST Crop Production Data directory."),
            "name": gettext("model data directory")
        }
    },
    "outputs": {
        "aggregate_results.csv": {
            "created_if": "aggregate_polygon_path",
            "about": "Model results aggregated to AOI polygons",
            "index_col": "FID",
            "columns": {
                "FID": {
                    "type": "integer",
                    "about": "FID of the AOI polygon"
                },
                "[CROP]_observed": {
                    "type": "number",
                    "units": u.metric_ton,
                    "about": (
                        "Observed production of the given crop within the polygon")
                },
                "[CROP]_yield_[PERCENTILE]": {
                    "type": "number",
                    "units": u.metric_ton,
                    "about": (
                        "Modeled production of the given crop within the "
                        "polygon at the given percentile")
                },
                **{
                    f"{nutrient_code}_observed": {
                        "about": f"Observed {nutrient} production within the polygon",
                        "type": "number",
                        "units": units
                    } for nutrient_code, nutrient, units in NUTRIENTS
                },
                **{
                    f"{nutrient_code}_[PERCENTILE]": {
                        "about": (
                            f"Modeled {nutrient} production within the polygon at"
                            "the given percentile"),
                        "type": "number",
                        "units": units
                    } for nutrient_code, nutrient, units in NUTRIENTS
                }
            }
        },
        "result_table.csv": {
            "about": "Model results aggregated by crop",
            "index_col": "crop",
            "columns": {
                "crop": {
                    "type": "freestyle_string",
                    "about": "Name of the crop"
                },
                "area (ha)": {
                    "type": "number",
                    "units": u.hectare,
                    "about": "Area covered by the crop"
                },
                "production_observed": {
                    "type": "number",
                    "units": u.metric_ton,
                    "about": "Observed crop production"
                },
                "production_[PERCENTILE]": {
                    "type": "number",
                    "units": u.metric_ton,
                    "about": "Modeled crop production at the given percentile"
                },
                **{
                    f"{nutrient_code}_observed": {
                        "about": f"Observed {nutrient} production from the crop",
                        "type": "number",
                        "units": units
                    } for nutrient_code, nutrient, units in NUTRIENTS
                },
                **{
                    f"{nutrient_code}_[PERCENTILE]": {
                        "about": (
                            f"Modeled {nutrient} production from the crop at"
                            "the given percentile"),
                        "type": "number",
                        "units": units
                    } for nutrient_code, nutrient, units in NUTRIENTS
                }
            }
        },
        "[CROP]_observed_production.tif": {
            "about": "Observed yield for the given crop",
            "bands": {1: {"type": "number", "units": u.metric_ton/u.hectare}}
        },
        "[CROP]_yield_[PERCENTILE]_production.tif": {
            "about": (
                "Modeled yield for the given crop at the given percentile"),
            "bands": {1: {"type": "number", "units": u.metric_ton/u.hectare}}
        },
        "intermediate": {
            "type": "directory",
            "contents": {
                "clipped_[CROP]_climate_bin_map.tif": {
                    "about": (
                        "Climate bin map for the given crop, clipped to the "
                        "LULC extent"),
                    "bands": {1: {"type": "integer"}}
                },
                "[CROP]_clipped_observed_yield.tif": {
                    "about": (
                        "Observed yield for the given crop, clipped to the "
                        "extend of the landcover map"),
                    "bands": {1: {
                        "type": "number", "units": u.metric_ton/u.hectare
                    }}
                },
                "[CROP]_interpolated_observed_yield.tif": {
                    "about": (
                        "Observed yield for the given crop, interpolated to "
                        "the resolution of the landcover map"),
                    "bands": {1: {
                        "type": "number", "units": u.metric_ton/u.hectare
                    }}
                },
                "[CROP]_yield_[PERCENTILE]_coarse_yield.tif": {
                    "about": (
                        "Percentile yield of the given crop, at the coarse "
                        "resolution of the climate bin map"),
                    "bands": {1: {
                        "type": "number", "units": u.metric_ton/u.hectare
                    }}
                },
                "[CROP]_yield_[PERCENTILE]_interpolated_yield.tif": {
                    "about": (
                        "Percentile yield of the given crop, interpolated to "
                        "the resolution of the landcover map"),
                    "bands": {1: {
                        "type": "number", "units": u.metric_ton/u.hectare
                    }}
                },
                "[CROP]_zeroed_observed_yield.tif": {
                    "about": (
                        "Observed yield for the given crop, with nodata "
                        "converted to 0"),
                    "bands": {1: {
                        "type": "number", "units": u.metric_ton/u.hectare
                    }}
                }
            }
        },
        "taskgraph_cache": spec.TASKGRAPH_DIR
    }
})

_INTERMEDIATE_OUTPUT_DIR = 'intermediate_output'

_YIELD_PERCENTILE_FIELD_PATTERN = 'yield_([^_]+)'
_GLOBAL_OBSERVED_YIELD_FILE_PATTERN = os.path.join(
    'observed_yield', '%s_yield_map.tif')  # crop_name
_EXTENDED_CLIMATE_BIN_FILE_PATTERN = os.path.join(
    'extended_climate_bin_maps', 'extendedclimatebins%s.tif')  # crop_name
_CLIMATE_PERCENTILE_TABLE_PATTERN = os.path.join(
    'climate_percentile_yield_tables',
    '%s_percentile_yield_table.csv')  # crop_name

# crop_name, yield_percentile_id
_INTERPOLATED_YIELD_PERCENTILE_FILE_PATTERN = os.path.join(
    _INTERMEDIATE_OUTPUT_DIR, '%s_%s_interpolated_yield%s.tif')

# crop_name, file_suffix
_CLIPPED_CLIMATE_BIN_FILE_PATTERN = os.path.join(
    _INTERMEDIATE_OUTPUT_DIR,
    'clipped_%s_climate_bin_map%s.tif')

# crop_name, yield_percentile_id, file_suffix
_COARSE_YIELD_PERCENTILE_FILE_PATTERN = os.path.join(
    _INTERMEDIATE_OUTPUT_DIR, '%s_%s_coarse_yield%s.tif')

# crop_name, yield_percentile_id, file_suffix
_PERCENTILE_CROP_PRODUCTION_FILE_PATTERN = os.path.join(
    '.', '%s_%s_production%s.tif')

# crop_name, file_suffix
_CLIPPED_OBSERVED_YIELD_FILE_PATTERN = os.path.join(
    _INTERMEDIATE_OUTPUT_DIR, '%s_clipped_observed_yield%s.tif')

# crop_name, file_suffix
_ZEROED_OBSERVED_YIELD_FILE_PATTERN = os.path.join(
    _INTERMEDIATE_OUTPUT_DIR, '%s_zeroed_observed_yield%s.tif')

# crop_name, file_suffix
_INTERPOLATED_OBSERVED_YIELD_FILE_PATTERN = os.path.join(
    _INTERMEDIATE_OUTPUT_DIR, '%s_interpolated_observed_yield%s.tif')

# crop_name, file_suffix
_OBSERVED_PRODUCTION_FILE_PATTERN = os.path.join(
    '.', '%s_observed_production%s.tif')

# file_suffix
_AGGREGATE_VECTOR_FILE_PATTERN = os.path.join(
    _INTERMEDIATE_OUTPUT_DIR, 'aggregate_vector%s.shp')

# file_suffix
_AGGREGATE_TABLE_FILE_PATTERN = os.path.join(
    '.', 'aggregate_results%s.csv')

_EXPECTED_NUTRIENT_TABLE_HEADERS = list(nutrient_units.keys())
_EXPECTED_LUCODE_TABLE_HEADER = 'lucode'
_NODATA_YIELD = -1


def execute(args):
    """Crop Production Percentile.

    This model will take a landcover (crop cover?) map and produce yields,
    production, and observed crop yields, a nutrient table, and a clipped
    observed map.

    Args:
        args['workspace_dir'] (string): output directory for intermediate,
            temporary, and final files
        args['results_suffix'] (string): (optional) string to append to any
            output file names
        args['landcover_raster_path'] (string): path to landcover raster
        args['landcover_to_crop_table_path'] (string): path to a table that
            converts landcover types to crop names that has two headers:

            * lucode: integer value corresponding to a landcover code in
              `args['landcover_raster_path']`.
            * crop_name: a string that must match one of the crops in
              args['model_data_path']/climate_bin_maps/[cropname]_*
              A ValueError is raised if strings don't match.

        args['aggregate_polygon_path'] (string): path to polygon shapefile
            that will be used to aggregate crop yields and total nutrient
            value. (optional, if value is None, then skipped)
        args['model_data_path'] (string): path to the InVEST Crop Production
            global data directory.  This model expects that the following
            directories are subdirectories of this path:

            * climate_bin_maps (contains [cropname]_climate_bin.tif files)
            * climate_percentile_yield (contains
              [cropname]_percentile_yield_table.csv files)

            Please see the InVEST user's guide chapter on crop production for
            details about how to download these data.
        args['n_workers'] (int): (optional) The number of worker processes to
            use for processing this model.  If omitted, computation will take
            place in the current process.

    Returns:
        None.

    """
    crop_to_landcover_df = MODEL_SPEC.get_input(
        'landcover_to_crop_table_path').get_validated_dataframe(
            args['landcover_to_crop_table_path'])

    lucodes_in_table = set(list(
        crop_to_landcover_df[_EXPECTED_LUCODE_TABLE_HEADER]))

    def update_unique_lucodes_in_raster(unique_codes, block):
        unique_codes.update(numpy.unique(block))
        return unique_codes

    unique_lucodes_in_raster = pygeoprocessing.raster_reduce(
        update_unique_lucodes_in_raster,
        (args['landcover_raster_path'], 1),
        set())

    lucodes_missing_from_raster = lucodes_in_table.difference(
        unique_lucodes_in_raster)
    if lucodes_missing_from_raster:
        LOGGER.warning(
            "The following lucodes are in the landcover to crop table but "
            f"aren't in the landcover raster: {lucodes_missing_from_raster}")

    lucodes_missing_from_table = unique_lucodes_in_raster.difference(
        lucodes_in_table)
    if lucodes_missing_from_table:
        LOGGER.warning(
            "The following lucodes are in the landcover raster but aren't "
            f"in the landcover to crop table: {lucodes_missing_from_table}")

    bad_crop_name_list = []
    for crop_name in crop_to_landcover_df.index:
        crop_climate_bin_raster_path = os.path.join(
            args['model_data_path'],
            _EXTENDED_CLIMATE_BIN_FILE_PATTERN % crop_name)
        if not os.path.exists(crop_climate_bin_raster_path):
            bad_crop_name_list.append(crop_name)
    if bad_crop_name_list:
        raise ValueError(
            "The following crop names were provided in %s but no such crops "
            "exist for this model: %s" % (
                args['landcover_to_crop_table_path'], bad_crop_name_list))

    file_suffix = utils.make_suffix_string(args, 'results_suffix')
    output_dir = os.path.join(args['workspace_dir'])
    utils.make_directories([
        output_dir, os.path.join(output_dir, _INTERMEDIATE_OUTPUT_DIR)])

    landcover_raster_info = pygeoprocessing.get_raster_info(
        args['landcover_raster_path'])
    pixel_area_ha = numpy.prod([
        abs(x) for x in landcover_raster_info['pixel_size']]) / 10000
    landcover_nodata = landcover_raster_info['nodata'][0]
    if landcover_nodata is None:
        LOGGER.warning(
            "%s does not have nodata value defined; "
            "assuming all pixel values are valid"
            % args['landcover_raster_path'])

    # Calculate lat/lng bounding box for landcover map
    wgs84srs = osr.SpatialReference()
    wgs84srs.ImportFromEPSG(4326)  # EPSG4326 is WGS84 lat/lng
    landcover_wgs84_bounding_box = pygeoprocessing.transform_bounding_box(
        landcover_raster_info['bounding_box'],
        landcover_raster_info['projection_wkt'], wgs84srs.ExportToWkt(),
        edge_samples=11)

    # Initialize a TaskGraph
    try:
        n_workers = int(args['n_workers'])
    except (KeyError, ValueError, TypeError):
        # KeyError when n_workers is not present in args
        # ValueError when n_workers is an empty string.
        # TypeError when n_workers is None.
        n_workers = -1  # Single process mode.
    task_graph = taskgraph.TaskGraph(
        os.path.join(output_dir, 'taskgraph_cache'), n_workers)
    dependent_task_list = []

    crop_lucode = None
    observed_yield_nodata = None
    for crop_name, row in crop_to_landcover_df.iterrows():
        crop_lucode = row[_EXPECTED_LUCODE_TABLE_HEADER]
        LOGGER.info("Processing crop %s", crop_name)
        crop_climate_bin_raster_path = os.path.join(
            args['model_data_path'],
            _EXTENDED_CLIMATE_BIN_FILE_PATTERN % crop_name)

        LOGGER.info(
            "Clipping global climate bin raster to landcover bounding box.")
        clipped_climate_bin_raster_path = os.path.join(
            output_dir, _CLIPPED_CLIMATE_BIN_FILE_PATTERN % (
                crop_name, file_suffix))
        crop_climate_bin_raster_info = pygeoprocessing.get_raster_info(
            crop_climate_bin_raster_path)
        crop_climate_bin_task = task_graph.add_task(
            func=pygeoprocessing.warp_raster,
            args=(crop_climate_bin_raster_path,
                  crop_climate_bin_raster_info['pixel_size'],
                  clipped_climate_bin_raster_path, 'near'),
            kwargs={'target_bb': landcover_wgs84_bounding_box},
            target_path_list=[clipped_climate_bin_raster_path],
            task_name='crop_climate_bin')
        dependent_task_list.append(crop_climate_bin_task)

        climate_percentile_yield_table_path = os.path.join(
            args['model_data_path'],
            _CLIMATE_PERCENTILE_TABLE_PATTERN % crop_name)
        crop_climate_percentile_df = MODEL_SPEC.get_input(
            'model_data_path').contents.get(
            'climate_percentile_yield_tables').contents.get(
            '[CROP]_percentile_yield_table.csv').get_validated_dataframe(
            climate_percentile_yield_table_path)
        yield_percentile_headers = [
            x for x in crop_climate_percentile_df.columns if x != 'climate_bin']

        reclassify_error_details = {
            'raster_name': f'{crop_name} Climate Bin',
            'column_name': 'climate_bin',
            'table_name': f'Climate {crop_name} Percentile Yield'}
        for yield_percentile_id in yield_percentile_headers:
            LOGGER.info("Map %s to climate bins.", yield_percentile_id)
            interpolated_yield_percentile_raster_path = os.path.join(
                output_dir,
                _INTERPOLATED_YIELD_PERCENTILE_FILE_PATTERN % (
                    crop_name, yield_percentile_id, file_suffix))
            bin_to_percentile_yield = (
                crop_climate_percentile_df[yield_percentile_id].to_dict())
            # reclassify nodata to a valid value of 0
            # we're assuming that the crop doesn't exist where there is no data
            # this is more likely than assuming the crop does exist, esp.
            # in the context of the provided climate bins map
            bin_to_percentile_yield[
                crop_climate_bin_raster_info['nodata'][0]] = 0
            coarse_yield_percentile_raster_path = os.path.join(
                output_dir,
                _COARSE_YIELD_PERCENTILE_FILE_PATTERN % (
                    crop_name, yield_percentile_id, file_suffix))
            create_coarse_yield_percentile_task = task_graph.add_task(
                func=utils.reclassify_raster,
                args=((clipped_climate_bin_raster_path, 1),
                      bin_to_percentile_yield,
                      coarse_yield_percentile_raster_path, gdal.GDT_Float32,
                      _NODATA_YIELD, reclassify_error_details),
                target_path_list=[coarse_yield_percentile_raster_path],
                dependent_task_list=[crop_climate_bin_task],
                task_name='create_coarse_yield_percentile_%s_%s' % (
                    crop_name, yield_percentile_id))
            dependent_task_list.append(create_coarse_yield_percentile_task)

            LOGGER.info(
                "Interpolate %s %s yield raster to landcover resolution.",
                crop_name, yield_percentile_id)
            create_interpolated_yield_percentile_task = task_graph.add_task(
                func=pygeoprocessing.warp_raster,
                args=(coarse_yield_percentile_raster_path,
                      landcover_raster_info['pixel_size'],
                      interpolated_yield_percentile_raster_path, 'cubicspline'),
                kwargs={'target_projection_wkt': landcover_raster_info['projection_wkt'],
                        'target_bb': landcover_raster_info['bounding_box']},
                target_path_list=[interpolated_yield_percentile_raster_path],
                dependent_task_list=[create_coarse_yield_percentile_task],
                task_name='create_interpolated_yield_percentile_%s_%s' % (
                    crop_name, yield_percentile_id))
            dependent_task_list.append(
                create_interpolated_yield_percentile_task)

            LOGGER.info(
                "Calculate yield for %s at %s", crop_name,
                yield_percentile_id)
            percentile_crop_production_raster_path = os.path.join(
                output_dir,
                _PERCENTILE_CROP_PRODUCTION_FILE_PATTERN % (
                    crop_name, yield_percentile_id, file_suffix))

            create_percentile_production_task = task_graph.add_task(
                func=calculate_crop_production,
                args=(
                    args['landcover_raster_path'],
                    interpolated_yield_percentile_raster_path,
                    crop_lucode,
                    percentile_crop_production_raster_path),
                target_path_list=[percentile_crop_production_raster_path],
                dependent_task_list=[
                    create_interpolated_yield_percentile_task],
                task_name='create_percentile_production_%s_%s' % (
                    crop_name, yield_percentile_id))
            dependent_task_list.append(create_percentile_production_task)

        LOGGER.info("Calculate observed yield for %s", crop_name)
        global_observed_yield_raster_path = os.path.join(
            args['model_data_path'],
            _GLOBAL_OBSERVED_YIELD_FILE_PATTERN % crop_name)
        global_observed_yield_raster_info = (
            pygeoprocessing.get_raster_info(
                global_observed_yield_raster_path))

        clipped_observed_yield_raster_path = os.path.join(
            output_dir, _CLIPPED_OBSERVED_YIELD_FILE_PATTERN % (
                crop_name, file_suffix))
        clip_global_observed_yield_task = task_graph.add_task(
            func=pygeoprocessing.warp_raster,
            args=(global_observed_yield_raster_path,
                  global_observed_yield_raster_info['pixel_size'],
                  clipped_observed_yield_raster_path, 'near'),
            kwargs={'target_bb': landcover_wgs84_bounding_box},
            target_path_list=[clipped_observed_yield_raster_path],
            task_name='clip_global_observed_yield_%s_' % crop_name)
        dependent_task_list.append(clip_global_observed_yield_task)

        observed_yield_nodata = (
            global_observed_yield_raster_info['nodata'][0])

        zeroed_observed_yield_raster_path = os.path.join(
            output_dir, _ZEROED_OBSERVED_YIELD_FILE_PATTERN % (
                crop_name, file_suffix))

        nodata_to_zero_for_observed_yield_task = task_graph.add_task(
            func=pygeoprocessing.raster_calculator,
            args=([(clipped_observed_yield_raster_path, 1),
                   (observed_yield_nodata, 'raw')],
                  _zero_observed_yield_op, zeroed_observed_yield_raster_path,
                  gdal.GDT_Float32, observed_yield_nodata),
            target_path_list=[zeroed_observed_yield_raster_path],
            dependent_task_list=[clip_global_observed_yield_task],
            task_name='nodata_to_zero_for_observed_yield_%s_' % crop_name)
        dependent_task_list.append(nodata_to_zero_for_observed_yield_task)

        interpolated_observed_yield_raster_path = os.path.join(
            output_dir, _INTERPOLATED_OBSERVED_YIELD_FILE_PATTERN % (
                crop_name, file_suffix))

        LOGGER.info(
            "Interpolating observed %s raster to landcover.", crop_name)
        interpolate_observed_yield_task = task_graph.add_task(
            func=pygeoprocessing.warp_raster,
            args=(zeroed_observed_yield_raster_path,
                  landcover_raster_info['pixel_size'],
                  interpolated_observed_yield_raster_path, 'cubicspline'),
            kwargs={'target_projection_wkt': landcover_raster_info['projection_wkt'],
                    'target_bb': landcover_raster_info['bounding_box']},
            target_path_list=[interpolated_observed_yield_raster_path],
            dependent_task_list=[nodata_to_zero_for_observed_yield_task],
            task_name='interpolate_observed_yield_to_lulc_%s' % crop_name)
        dependent_task_list.append(interpolate_observed_yield_task)

        observed_production_raster_path = os.path.join(
            output_dir, _OBSERVED_PRODUCTION_FILE_PATTERN % (
                crop_name, file_suffix))

        calculate_observed_production_task = task_graph.add_task(
            func=pygeoprocessing.raster_calculator,
            args=([(args['landcover_raster_path'], 1),
                   (interpolated_observed_yield_raster_path, 1),
                   (observed_yield_nodata, 'raw'), (landcover_nodata, 'raw'),
                   (crop_lucode, 'raw')],
                  _mask_observed_yield_op, observed_production_raster_path,
                  gdal.GDT_Float32, observed_yield_nodata),
            target_path_list=[observed_production_raster_path],
            dependent_task_list=[interpolate_observed_yield_task],
            task_name='calculate_observed_production_%s' % crop_name)
        dependent_task_list.append(calculate_observed_production_task)

    # both 'crop_nutrient.csv' and 'crop' are known data/header values for
    # this model data.
    nutrient_df = MODEL_SPEC.get_input(
        'model_data_path').contents.get(
        'crop_nutrient.csv').get_validated_dataframe(
            os.path.join(args['model_data_path'], 'crop_nutrient.csv'))

    result_table_path = os.path.join(
        output_dir, 'result_table%s.csv' % file_suffix)

    crop_names = crop_to_landcover_df.index.to_list()
    _ = task_graph.add_task(
        func=tabulate_results,
        args=(nutrient_df, yield_percentile_headers,
              crop_names, pixel_area_ha,
              args['landcover_raster_path'], landcover_nodata,
              output_dir, file_suffix, result_table_path),
        target_path_list=[result_table_path],
        dependent_task_list=dependent_task_list,
        task_name='tabulate_results')

    if ('aggregate_polygon_path' in args and
            args['aggregate_polygon_path'] not in ['', None]):
        LOGGER.info("aggregating result over query polygon")
        target_aggregate_vector_path = os.path.join(
            output_dir, _AGGREGATE_VECTOR_FILE_PATTERN % (file_suffix))
        aggregate_results_table_path = os.path.join(
            output_dir, _AGGREGATE_TABLE_FILE_PATTERN % file_suffix)
        _ = task_graph.add_task(
            func=aggregate_to_polygons,
            args=(args['aggregate_polygon_path'],
                  target_aggregate_vector_path,
                  landcover_raster_info['projection_wkt'],
                  crop_names, nutrient_df,
                  yield_percentile_headers, pixel_area_ha, output_dir,
                  file_suffix, aggregate_results_table_path),
            target_path_list=[target_aggregate_vector_path,
                              aggregate_results_table_path],
            dependent_task_list=dependent_task_list,
            task_name='aggregate_results_to_polygons')

    task_graph.close()
    task_graph.join()


def calculate_crop_production(lulc_path, yield_path, crop_lucode,
                              target_path):
    """Calculate crop production for a particular crop.

    The resulting production value is:

    - nodata, where either the LULC or yield input has nodata
    - 0, where the LULC does not match the given LULC code
    - yield (in Mg/ha), where the given LULC code exists

    Args:
        lulc_path (str): path to a raster of LULC codes
        yield_path (str): path of a raster of yields for the crop identified
            by ``crop_lucode``, in units per hectare
        crop_lucode (int): LULC code that identifies the crop of interest in
            the ``lulc_path`` raster.
        target_path (str): Path to write the output crop production raster

    Returns:
        None
    """
    pygeoprocessing.raster_map(
        op=lambda lulc, _yield: numpy.where(
            lulc == crop_lucode, _yield, 0),
        rasters=[lulc_path, yield_path],
        target_path=target_path,
        target_nodata=_NODATA_YIELD)


def _zero_observed_yield_op(observed_yield_array, observed_yield_nodata):
    """Reclassify observed_yield nodata to zero.

    Args:
        observed_yield_array (numpy.ndarray): raster values
        observed_yield_nodata (float): raster nodata value

    Returns:
        numpy.ndarray with observed yield values

    """
    result = numpy.empty(
        observed_yield_array.shape, dtype=numpy.float32)
    result[:] = 0
    valid_mask = slice(None)
    if observed_yield_nodata is not None:
        valid_mask = ~pygeoprocessing.array_equals_nodata(
            observed_yield_array, observed_yield_nodata)
    result[valid_mask] = observed_yield_array[valid_mask]
    return result


def _mask_observed_yield_op(
        lulc_array, observed_yield_array, observed_yield_nodata,
        landcover_nodata, crop_lucode):
    """Mask total observed yield to crop lulc type.

    Args:
        lulc_array (numpy.ndarray): landcover raster values
        observed_yield_array (numpy.ndarray): yield raster values
        observed_yield_nodata (float): yield raster nodata value
        landcover_nodata (float): landcover raster nodata value
        crop_lucode (int): code used to mask in the current crop

    Returns:
        numpy.ndarray with float values of yields masked to crop_lucode

    """
    result = numpy.empty(lulc_array.shape, dtype=numpy.float32)
    if landcover_nodata is not None:
        result[:] = observed_yield_nodata
        valid_mask = ~pygeoprocessing.array_equals_nodata(lulc_array,
                                                          landcover_nodata)
        result[valid_mask] = 0
    else:
        result[:] = 0
    lulc_mask = lulc_array == crop_lucode
    result[lulc_mask] = observed_yield_array[lulc_mask]
    return result


def tabulate_results(
        nutrient_df, yield_percentile_headers,
        crop_names, pixel_area_ha, landcover_raster_path,
        landcover_nodata, output_dir, file_suffix, target_table_path):
    """Write table with total yield and nutrient results by crop.

    This function includes all the operations that write to results_table.csv.

    Args:
        nutrient_df (pandas.DataFrame): a table of nutrient values by crop
        yield_percentile_headers (list): list of strings indicating percentiles
            at which yield was calculated.
        crop_names (list): list of crop names
        pixel_area_ha (float): area of lulc raster cells (hectares)
        landcover_raster_path (string): path to landcover raster
        landcover_nodata (float): landcover raster nodata value
        output_dir (string): the file path to the output workspace.
        file_suffix (string): string to append to any output filenames.
        target_table_path (string): path to 'result_table.csv' in the output
            workspace

    Returns:
        None

    """
    LOGGER.info("Generating report table")
    production_percentile_headers = [
        'production_' + re.match(
            _YIELD_PERCENTILE_FIELD_PATTERN,
            yield_percentile_id).group(1) for yield_percentile_id in sorted(
                yield_percentile_headers)]
    nutrient_headers = [
        nutrient_id + '_' + re.match(
            _YIELD_PERCENTILE_FIELD_PATTERN,
            yield_percentile_id).group(1)
        for nutrient_id in _EXPECTED_NUTRIENT_TABLE_HEADERS
        for yield_percentile_id in sorted(yield_percentile_headers) + [
            'yield_observed']]

    # Since pixel values in observed and percentile rasters are Mg/(ha•yr),
    # raster sums are (Mg•px)/(ha•yr). Before recording sums in
    # production_lookup dictionary, convert to Mg/yr by multiplying by ha/px.

    with open(target_table_path, 'w') as result_table:
        result_table.write(
            'crop,area (ha),' + 'production_observed,' +
            ','.join(production_percentile_headers) + ',' + ','.join(
                nutrient_headers) + '\n')
        for crop_name in sorted(crop_names):
            result_table.write(crop_name)
            production_lookup = {}
            production_pixel_count = 0
            yield_sum = 0
            observed_production_raster_path = os.path.join(
                output_dir,
                _OBSERVED_PRODUCTION_FILE_PATTERN % (
                    crop_name, file_suffix))

            LOGGER.info(
                "Calculating production area and summing observed yield.")
            observed_yield_nodata = pygeoprocessing.get_raster_info(
                observed_production_raster_path)['nodata'][0]
            for _, yield_block in pygeoprocessing.iterblocks(
                    (observed_production_raster_path, 1)):

                # make a valid mask showing which pixels are not nodata
                # if nodata value undefined, assume all pixels are valid
                valid_mask = numpy.full(yield_block.shape, True)
                if observed_yield_nodata is not None:
                    valid_mask = ~pygeoprocessing.array_equals_nodata(
                        yield_block, observed_yield_nodata)
                production_pixel_count += numpy.count_nonzero(
                    valid_mask & (yield_block > 0))
                yield_sum += numpy.sum(yield_block[valid_mask])
            yield_sum *= pixel_area_ha
            production_area = production_pixel_count * pixel_area_ha
            production_lookup['observed'] = yield_sum
            result_table.write(',%f' % production_area)
            result_table.write(",%f" % yield_sum)

            for yield_percentile_id in sorted(yield_percentile_headers):
                yield_percentile_raster_path = os.path.join(
                    output_dir,
                    _PERCENTILE_CROP_PRODUCTION_FILE_PATTERN % (
                        crop_name, yield_percentile_id, file_suffix))
                yield_sum = 0
                for _, yield_block in pygeoprocessing.iterblocks(
                        (yield_percentile_raster_path, 1)):
                    # _NODATA_YIELD will always have a value (defined above)
                    yield_sum += numpy.sum(
                        yield_block[~pygeoprocessing.array_equals_nodata(
                            yield_block, _NODATA_YIELD)])
                yield_sum *= pixel_area_ha
                production_lookup[yield_percentile_id] = yield_sum
                result_table.write(",%f" % yield_sum)

            # convert 100g to Mg and fraction left over from refuse
            nutrient_factor = 1e4 * (
                1 - nutrient_df['percentrefuse'][crop_name] / 100)
            for nutrient_id in _EXPECTED_NUTRIENT_TABLE_HEADERS:
                for yield_percentile_id in sorted(yield_percentile_headers):
                    total_nutrient = (
                        nutrient_factor *
                        production_lookup[yield_percentile_id] *
                        nutrient_df[nutrient_id][crop_name])
                    result_table.write(",%f" % (total_nutrient))
                result_table.write(
                    ",%f" % (
                        nutrient_factor *
                        production_lookup['observed'] *
                        nutrient_df[nutrient_id][crop_name]))
            result_table.write('\n')

        total_area = 0
        for _, band_values in pygeoprocessing.iterblocks(
                (landcover_raster_path, 1)):
            if landcover_nodata is not None:
                total_area += numpy.count_nonzero(
                    ~pygeoprocessing.array_equals_nodata(band_values,
                                                         landcover_nodata))
            else:
                total_area += band_values.size
        result_table.write(
            '\n,total area (both crop and non-crop)\n,%f\n' % (
                total_area * pixel_area_ha))


def aggregate_to_polygons(
        base_aggregate_vector_path, target_aggregate_vector_path,
        landcover_raster_projection, crop_names, nutrient_df,
        yield_percentile_headers, pixel_area_ha, output_dir, file_suffix,
        target_aggregate_table_path):
    """Write table with aggregate results of yield and nutrient values.

    Use zonal statistics to summarize total observed and interpolated
    production and nutrient information for each polygon in
    base_aggregate_vector_path.

    Args:
        base_aggregate_vector_path (string): path to polygon vector
        target_aggregate_vector_path (string):
            path to re-projected copy of polygon vector
        landcover_raster_projection (string): a WKT projection string
        crop_names (list): list of crop names
        nutrient_df (pandas.DataFrame): a table of nutrient values by crop
        yield_percentile_headers (list): list of strings indicating percentiles
            at which yield was calculated.
        pixel_area_ha (float): area of lulc raster cells (hectares)
        output_dir (string): the file path to the output workspace.
        file_suffix (string): string to append to any output filenames.
        target_aggregate_table_path (string): path to 'aggregate_results.csv'
            in the output workspace

    Returns:
        None

    """
    # reproject polygon to LULC's projection
    pygeoprocessing.reproject_vector(
        base_aggregate_vector_path,
        landcover_raster_projection,
        target_aggregate_vector_path,
        driver_name='ESRI Shapefile')

    # Since pixel values are Mg/(ha•yr), zonal stats sum is (Mg•px)/(ha•yr).
    # Before writing sum to results tables or when using sum to calculate
    # nutrient yields, convert to Mg/yr by multiplying by ha/px.

    # loop over every crop and query with pgp function
    total_yield_lookup = {}
    total_nutrient_table = collections.defaultdict(
        lambda: collections.defaultdict(lambda: collections.defaultdict(
            float)))
    for crop_name in crop_names:
        # convert 100g to Mg and fraction left over from refuse
        nutrient_factor = 1e4 * (
            1 - nutrient_df['percentrefuse'][crop_name] / 100)
        # loop over percentiles
        for yield_percentile_id in yield_percentile_headers:
            percentile_crop_production_raster_path = os.path.join(
                output_dir,
                _PERCENTILE_CROP_PRODUCTION_FILE_PATTERN % (
                    crop_name, yield_percentile_id, file_suffix))
            LOGGER.info(
                "Calculating zonal stats for %s  %s", crop_name,
                yield_percentile_id)
            total_yield_lookup['%s_%s' % (
                crop_name, yield_percentile_id)] = (
                    pygeoprocessing.zonal_statistics(
                        (percentile_crop_production_raster_path, 1),
                        target_aggregate_vector_path))

            for nutrient_id in _EXPECTED_NUTRIENT_TABLE_HEADERS:
                for id_index in total_yield_lookup['%s_%s' % (
                        crop_name, yield_percentile_id)]:
                    total_nutrient_table[nutrient_id][
                        yield_percentile_id][id_index] += (
                            nutrient_factor
                            * total_yield_lookup[
                                    '%s_%s' % (crop_name, yield_percentile_id)
                                ][id_index]['sum']
                            * pixel_area_ha
                            * nutrient_df[nutrient_id][crop_name])

        # process observed
        observed_yield_path = os.path.join(
            output_dir, _OBSERVED_PRODUCTION_FILE_PATTERN % (
                crop_name, file_suffix))
        total_yield_lookup[f'{crop_name}_observed'] = (
            pygeoprocessing.zonal_statistics(
                (observed_yield_path, 1),
                target_aggregate_vector_path))
        for nutrient_id in _EXPECTED_NUTRIENT_TABLE_HEADERS:
            for id_index in total_yield_lookup[f'{crop_name}_observed']:
                total_nutrient_table[
                    nutrient_id]['observed'][id_index] += (
                        nutrient_factor
                        * total_yield_lookup[
                            f'{crop_name}_observed'][id_index]['sum']
                        * pixel_area_ha
                        * nutrient_df[nutrient_id][crop_name])

    # report everything to a table
    with open(target_aggregate_table_path, 'w') as aggregate_table:
        # write header
        aggregate_table.write('FID,')
        aggregate_table.write(','.join(sorted(total_yield_lookup)) + ',')
        aggregate_table.write(
            ','.join([
                '%s_%s' % (nutrient_id, model_type)
                for nutrient_id in _EXPECTED_NUTRIENT_TABLE_HEADERS
                for model_type in sorted(
                    list(total_nutrient_table.values())[0])]))
        aggregate_table.write('\n')

        # iterate by polygon index
        for id_index in list(total_yield_lookup.values())[0]:
            aggregate_table.write('%s,' % id_index)
            aggregate_table.write(','.join([
                str(total_yield_lookup[yield_header][id_index]['sum']
                    * pixel_area_ha)
                for yield_header in sorted(total_yield_lookup)]))

            for nutrient_id in _EXPECTED_NUTRIENT_TABLE_HEADERS:
                for model_type in sorted(
                        list(total_nutrient_table.values())[0]):
                    aggregate_table.write(
                        ',%s' % total_nutrient_table[
                            nutrient_id][model_type][id_index])
            aggregate_table.write('\n')


# This decorator ensures the input arguments are formatted for InVEST
@validation.invest_validator
def validate(args, limit_to=None):
    """Validate args to ensure they conform to `execute`'s contract.

    Args:
        args (dict): dictionary of key(str)/value pairs where keys and
            values are specified in `execute` docstring.
        limit_to (str): (optional) if not None indicates that validation
            should only occur on the args[limit_to] value. The intent that
            individual key validation could be significantly less expensive
            than validating the entire `args` dictionary.

    Returns:
        list of ([invalid key_a, invalid_keyb, ...], 'warning/error message')
            tuples. Where an entry indicates that the invalid keys caused
            the error message in the second part of the tuple. This should
            be an empty list if validation succeeds.
    """
    return validation.validate(args, MODEL_SPEC)
