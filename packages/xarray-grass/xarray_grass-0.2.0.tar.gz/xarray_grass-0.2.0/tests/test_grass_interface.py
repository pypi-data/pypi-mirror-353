from collections import namedtuple
from datetime import datetime

import pytest
import numpy as np

# Needed to import grass modules
import grass_session  # noqa: F401
import grass.script as gs
import grass.exceptions as gexceptions

from xarray_grass import GrassInterface


ACTUAL_STRDS = "LST_Day_monthly@modis_lst"
ACTUAL_RASTER_MAP = "elevation@PERMANENT"
RELATIVE_STR3DS = "test_str3ds_relative"


def test_no_grass_session():
    with pytest.raises(RuntimeError):
        GrassInterface()


@pytest.mark.usefixtures("grass_session_fixture")
class TestGrassInterface:
    def test_grass_dtype(self, grass_i) -> None:
        """Test the dtype conversion frm numpy to GRASS."""
        assert grass_i.grass_dtype("bool_") == "CELL"
        assert grass_i.grass_dtype("int_") == "CELL"
        assert grass_i.grass_dtype("int8") == "CELL"
        assert grass_i.grass_dtype("int16") == "CELL"
        assert grass_i.grass_dtype("int32") == "CELL"
        assert grass_i.grass_dtype("intc") == "CELL"
        assert grass_i.grass_dtype("intp") == "CELL"
        assert grass_i.grass_dtype("uint8") == "CELL"
        assert grass_i.grass_dtype("uint16") == "CELL"
        assert grass_i.grass_dtype("uint32") == "CELL"
        assert grass_i.grass_dtype("float32") == "FCELL"
        assert grass_i.grass_dtype("float64") == "DCELL"
        with pytest.raises(ValueError):
            grass_i.grass_dtype("bool")
            grass_i.grass_dtype("int")
            grass_i.grass_dtype("float")

    def test_get_region(self, grass_i):
        """Test the get_region method."""
        region = grass_i.get_region()
        assert region is not None
        assert region.rows > 0
        assert region.cols > 0
        assert region.n > region.s
        assert region.e > region.w
        assert region.t > region.b

    def test_is_latlon(self):
        assert GrassInterface.is_latlon() is False

    def test_get_id_from_name(self):
        assert GrassInterface.get_id_from_name("test_map") == "test_map@PERMANENT"
        assert (
            GrassInterface.get_id_from_name("test_map@PERMANENT")
            == "test_map@PERMANENT"
        )
        assert GrassInterface.get_id_from_name("") == "@PERMANENT"
        with pytest.raises(TypeError):
            GrassInterface.get_id_from_name(False)
            GrassInterface.get_id_from_name(12.4)
            GrassInterface.get_id_from_name(4)

    def test_get_name_from_id(self):
        assert GrassInterface.get_name_from_id("test_map") == "test_map"
        assert GrassInterface.get_name_from_id("test_map@PERMANENT") == "test_map"
        assert GrassInterface.get_name_from_id("@PERMANENT") == ""
        assert GrassInterface.get_name_from_id("") == ""
        with pytest.raises(TypeError):
            GrassInterface.get_name_from_id(False)
            GrassInterface.get_name_from_id(2.4)
            GrassInterface.get_name_from_id(4)

    def test_name_is_stdrs(self, grass_i):
        assert grass_i.name_is_strds(ACTUAL_STRDS) is True
        assert grass_i.name_is_strds(ACTUAL_RASTER_MAP) is False
        assert grass_i.name_is_strds("not_a_real_strds@PERMANENT") is False
        with pytest.raises(gexceptions.FatalError):
            grass_i.name_is_strds("not_a_real_strds@NOT_A_MAPSET")
            grass_i.name_is_strds("not_a_real_strds")

    def test_name_is_raster(self, grass_i):
        assert grass_i.name_is_raster(ACTUAL_RASTER_MAP) is True
        assert grass_i.name_is_raster(ACTUAL_STRDS) is False
        assert grass_i.name_is_raster("not_a_real_map@PERMANENT") is False
        assert grass_i.name_is_raster("not_a_real_map@NOT_A_MAPSET") is False
        assert grass_i.name_is_raster("not_a_real_map") is False

    def test_get_proj_str(self):
        proj_str = GrassInterface.get_proj_str()
        ref_str = gs.read_command("g.proj", flags="jf")
        assert proj_str == ref_str.replace("\n", "")
        assert isinstance(proj_str, str)

    def test_get_crs_wkt_str(self):
        crs_str = GrassInterface.get_crs_wkt_str()
        ref_str = gs.read_command("g.proj", flags="wf")
        assert crs_str == ref_str.replace("\n", "")
        assert isinstance(crs_str, str)

    def test_has_mask(self):
        assert GrassInterface.has_mask() is False
        gs.run_command("r.mask", quiet=True, raster=ACTUAL_RASTER_MAP)
        assert GrassInterface.has_mask() is True
        gs.run_command("r.mask", flags="r")
        assert GrassInterface.has_mask() is False

    def test_list_strds(self):
        strds_list = GrassInterface.list_strds()
        assert strds_list == [ACTUAL_STRDS]

    def test_get_stds_infos(self, grass_i):
        strds_infos = grass_i.get_stds_infos(ACTUAL_STRDS, stds_type="strds")
        assert strds_infos.id == ACTUAL_STRDS
        assert strds_infos.temporal_type == "absolute"
        assert strds_infos.time_unit is None
        assert strds_infos.start_time == datetime(2015, 1, 1, 0, 0)
        assert strds_infos.end_time == datetime(2017, 1, 1, 0, 0)
        assert strds_infos.time_granularity == "1 month"
        assert strds_infos.north == pytest.approx(760180.12411493)
        assert strds_infos.south == pytest.approx(-415819.87588507)
        assert strds_infos.east == pytest.approx(1550934.46411531)
        assert strds_infos.west == pytest.approx(-448265.53588469)
        assert strds_infos.top == 0.0
        assert strds_infos.bottom == 0.0

    def test_list_maps_in_strds(self, grass_i):
        map_list = grass_i.list_maps_in_strds(ACTUAL_STRDS)
        assert len(map_list) == 24

    def test_list_maps_in_str3ds(self, grass_i):
        map_list = grass_i.list_maps_in_str3ds(RELATIVE_STR3DS)
        assert len(map_list) == 3

    def test_read_raster_map(self, grass_i):
        np_map = grass_i.read_raster_map(ACTUAL_RASTER_MAP)
        region = grass_i.get_region()
        assert np_map is not None
        assert np_map.shape == (region.rows, region.cols)
        assert np_map.dtype == "float32"
        assert not np.isnan(np_map).any()

    def test_write_raster_map(self, grass_i):
        rng = np.random.default_rng()
        # tests cases
        TestCase = namedtuple("TestCase", ["np_dtype", "g_dtype", "map_name"])
        test_cases = [
            TestCase(np_dtype=np.uint8, g_dtype="CELL", map_name="test_write_int"),
            TestCase(np_dtype=np.float32, g_dtype="FCELL", map_name="test_write_f32"),
            TestCase(np_dtype=np.float64, g_dtype="DCELL", map_name="test_write_f64"),
        ]
        region = grass_i.get_region()
        for test_case in test_cases:
            if test_case.g_dtype == "CELL":
                np_array_good = rng.integers(
                    0,
                    255,
                    size=(region.rows, region.cols),
                    dtype=test_case.np_dtype,
                )
                np_array_bad = rng.integers(
                    0, 255, size=(5, 2), dtype=test_case.np_dtype
                )
            else:
                np_array_bad = rng.random(size=(20, 23), dtype=test_case.np_dtype)
                np_array_good = rng.random(
                    size=(region.rows, region.cols), dtype=test_case.np_dtype
                )
            with pytest.raises(ValueError):
                grass_i.write_raster_map(np_array_bad, test_case.map_name)
            grass_i.write_raster_map(np_array_good, test_case.map_name)
            map_info = gs.parse_command(
                "r.info", flags="g", map=f"{test_case.map_name}@PERMANENT"
            )
            assert map_info["rows"] == str(region.rows)
            assert map_info["cols"] == str(region.cols)
            assert map_info["datatype"] == test_case.g_dtype
            # remove map
            gs.run_command(
                "g.remove", flags="f", type="raster", name=test_case.map_name
            )

    def test_register_maps_in_stds(self, grass_i):
        rng = np.random.default_rng()
        region = grass_i.get_region()
        np_array = rng.random(size=(region.rows, region.cols), dtype="float32")
        grass_i.write_raster_map(np_array, "test_temporal_map1")
        grass_i.write_raster_map(np_array, "test_temporal_map2")
        maps_list = [
            ("test_temporal_map1", datetime(2023, 1, 1)),
            ("test_temporal_map2", datetime(2023, 2, 1)),
        ]
        stds_name = "test_stds"
        grass_i.register_maps_in_stds(
            stds_title="test_stds_title",
            stds_name=stds_name,
            stds_desc="test description of a STRDS",
            semantic="mean",
            map_list=maps_list,
            t_type="absolute",
        )
        strds_info = gs.parse_command(
            "t.info",
            flags="g",
            type="strds",
            input=f"{stds_name}@PERMANENT",
        )
        print(strds_info)
        assert strds_info["name"] == stds_name
        assert strds_info["mapset"] == "PERMANENT"
        assert strds_info["id"] == f"{stds_name}@PERMANENT"
        assert strds_info["semantic_type"] == "mean"
        assert strds_info["temporal_type"] == "absolute"
        assert strds_info["number_of_maps"] == "2"
        # remove extra single quotes from the returned string
        assert strds_info["start_time"].strip("'") == str(datetime(2023, 1, 1))
        assert strds_info["end_time"].strip("'") == str(datetime(2023, 2, 1))
        # clean-up
        for map_name in ["test_temporal_map1", "test_temporal_map2"]:
            gs.run_command("g.remove", flags="f", type="raster", name=map_name)
        gs.run_command("t.remove", type="strds", input=stds_name, flags="f")
