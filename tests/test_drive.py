import pytest

from skipy.GCP import DriveService


class TestDriveService:
    def test_init(self):
        with pytest.raises(ValueError) as e:
            DriveService()
        assert (
            str(e.value)
            == "Either service_account_file or service_account_info must be provided."
        )
