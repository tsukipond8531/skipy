import pytest

from skipy.GCP import SheetService


class TestSheetService:
    def test_init(self):
        with pytest.raises(ValueError) as e:
            SheetService(service_account_info=None)
        assert (
            str(e.value)
            == "Either service_account_file or service_account_info must be provided."
        )
