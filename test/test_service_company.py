import pytest
from unittest.mock import MagicMock
from services import CompanyService


class TestCompanyService:

    @pytest.fixture(autouse=True)
    def setup_class(self, mocker):
        mocker.patch.dict("os.environ", {"STRIPE_API": "stripe_api"})

        # Patch Firebase initialization
        mocker.patch('firebase_admin.firestore.client')
        #self.mock_firebase_init = self.firebase_init_patch.start()

        self.mock_user_dao = mocker.patch("dao.UserDao")
        self.mock_payroll_dao = mocker.patch("dao.PayrollDao")
        self.mock_stripe_services = mocker.patch("services.StripeService")
        self.company_service = CompanyService("test_code")

    #read tutors
    def test_read_tutors_success(self):
        pass
