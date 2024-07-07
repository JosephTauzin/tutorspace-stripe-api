from entities import Membership, Subscription, Payroll, Response, PaymentSession, AdminPayout, StudentDebt, TutorPayout, TutorNotFound, TutorUser, Coupon

definitions = {
    'Membership': {
        'type': 'object',
        'properties': Membership.model_json_schema().get("properties")
    },
    'Subscription': {
        'type': 'object',
        'properties': Subscription.model_json_schema().get("properties")
    },
    'Payroll': {
        'type': 'object',
        'properties': Payroll.model_json_schema().get("properties")
    },
    'Response': {
        'type': 'object',
        'properties': Response.model_json_schema().get("properties")
    },
    'PaymentSession': {
        'type': 'object',
        'properties': PaymentSession.model_json_schema().get("properties")
    },
    'AdminPayout': {
        'type': 'object',
        'properties': AdminPayout.model_json_schema().get("properties")
    },
    'StudentDebt': {
        'type': 'object',
        'properties': StudentDebt.model_json_schema().get("properties")
    },
    'TutorPayout': {
        'type': 'object',
        'properties': TutorPayout.model_json_schema().get("properties")
    },
    'TutorNotFound': {
        'type': 'object',
        'properties': TutorNotFound.model_json_schema().get("properties")
    },
    'TutorUser': {
        'type': 'object',
        'properties': TutorUser.model_json_schema().get("properties")
    },
    'Coupon': {
        'type': 'object',
        'properties': Coupon.model_json_schema().get("properties")
    }
}

swagger_template = {
    'swagger': '2.0',
    'info': {
        'title': 'Stripe API',
        'description': '',
        'version': '1.0.0'
    },
    'basePath': '/',
    'schemes': [
        'http'
    ],
    'definitions': definitions
}
