"""test the __main__ module"""

import io

from importlib.metadata import PackageNotFoundError
from unittest.mock import call, patch

from ncw import __main__ as ncw_main

from . import test_base as tb


class Main(tb.VerboseTestCase):
    """main() function"""

    # pylint: disable=protected-access ; makes sense in test cases

    @patch("importlib.metadata")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_installed_with_version(self, mock_stdout, mock_metadata):
        """call with version argument, simulation of an installed package"""
        mock_metadata.version.return_value = "1.2.3"
        with patch("sys.argv", new=["ncw", "--version"]):
            self.assertRaises(SystemExit, ncw_main.main)
        #
        self.assertEqual(mock_stdout.getvalue(), "1.2.3\n")
        mock_metadata.version.assert_called_with(ncw_main._PACKAGE_NAME)

    @patch.object(ncw_main, "get_metadata_version")
    @patch("importlib.metadata.version")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_notinstalled_with_version_from_metadata(
        self, mock_stdout, mock_il_metadata_version, mock_gmv
    ):
        """call with version argument on non-installed package"""
        gmv_answer = "9.8.7 - directly from pyproject.toml"
        mock_il_metadata_version.side_effect = PackageNotFoundError("xyz")
        mock_gmv.return_value = gmv_answer
        with patch("sys.argv", new=["ncw", "--version"]):
            self.assertRaises(SystemExit, ncw_main.main)
        #
        self.assertEqual(mock_stdout.getvalue(), f"{gmv_answer}\n")
        mock_il_metadata_version.assert_called_with(ncw_main._PACKAGE_NAME)
        mock_gmv.assert_called_with()

    @patch("importlib.metadata.version")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_without_arguments(self, mock_stdout, mock_il_metadata_version):
        """call without arguments"""
        mock_il_metadata_version.return_value = "1.2.3"
        with patch("sys.argv", new=["ncw"]):
            ncw_main.main()
            self.assertEqual(mock_stdout.getvalue(), f"{ncw_main._INFO_TEXT}\n")
        #
        mock_il_metadata_version.assert_called_with(ncw_main._PACKAGE_NAME)


class GetMetadataVersion(tb.VerboseTestCase):
    """get_metadata_version() function"""

    @patch.object(ncw_main, "get_file_contents")
    def test_version_data_ok(self, mock_gfc):
        """call with version argument on non-installed package"""
        metadata_file = "metafile"
        mocked_version = "45.6"
        mock_gfc.return_value = (
            f'[whatever]\n\nversion = "{mocked_version}"\nxyz = "..."'
        )
        self.assertEqual(
            ncw_main.get_metadata_version(metadata_file, up_dirs=7),
            f"{mocked_version} (read directly from {metadata_file})",
        )
        mock_gfc.assert_called_with(metadata_file, up_dirs=7)

    @patch.object(ncw_main, "get_file_contents")
    def test_no_version_info(self, mock_gfc):
        """call with version argument on non-installed package"""
        metadata_file = "metafile_x"
        mock_gfc.side_effect = '[whatever]\n\n\nxyz = "..."'
        self.assertEqual(
            ncw_main.get_metadata_version(metadata_file, up_dirs=5),
            f"Error: no version information in metadata from {metadata_file}",
        )
        mock_gfc.assert_called_with(metadata_file, up_dirs=5)

    @patch.object(ncw_main, "get_file_contents")
    def test_file_io_error(self, mock_gfc):
        """call with version argument on non-installed package"""
        metadata_file = "metafile_y"
        mock_gfc.side_effect = IOError("weird reason")
        self.assertEqual(
            ncw_main.get_metadata_version(metadata_file, up_dirs=1), "weird reason"
        )
        mock_gfc.assert_called_with(metadata_file, up_dirs=1)


class GetFileContents(tb.VerboseTestCase):
    """get_file_contents() function"""

    @patch("pathlib.Path")
    def test_levels_up(self, mock_path):
        """Call with an arbitrary number"""
        # pylint: disable=unnecessary-dunder-call ; in mock context
        mock_path().resolve().parent.parent.__truediv__().read_text.return_value = (
            "dummy text"
        )
        self.assertEqual(
            ncw_main.get_file_contents("dummy-file", up_dirs=2),
            "dummy text",
        )
        self.assertListEqual(
            mock_path.mock_calls,
            [
                # return value assignment
                call(),
                call().resolve(),
                call().resolve().parent.parent.__truediv__(),
                # Inside the tested function
                call(ncw_main.__file__),
                call().resolve(),
                call().resolve().parent.parent.__truediv__("dummy-file"),
                call()
                .resolve()
                .parent.parent.__truediv__()
                .read_text(encoding="utf-8"),
            ],
        )
