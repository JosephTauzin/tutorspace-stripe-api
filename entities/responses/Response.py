import inspect
import logging
import traceback
from typing import Any

from pydantic import BaseModel

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class Response(BaseModel):
    success: bool = False  #status of the operation True/False
    message: Any = ""  #error/informative message
    response: Any = {}  #Response object with the result of the operation
    response_list: list = []  #Response list, a list of dict or objects, with the result of the operation

    class Config:
        arbitrary_types_allowed = True

    def __setattr__(self, key, value):
        if (key == "message"):
            current_frame = inspect.currentframe().f_back.f_back
            file_name = inspect.getfile(current_frame)
            logger.error("Full traceback in %s: %s", file_name, traceback.format_exc())
            value = str(value)
        super().__setattr__(key, value)

