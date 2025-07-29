import logging
import asyncio

import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.requests import Request
from starlette_admin.contrib.mongoengine import Admin, ModelView
from starlette_admin.actions import action
from starlette_admin.exceptions import ActionFailed
from mongoengine import Document, StringField
from kombu import Connection

from wiederverwendbar.mongoengine import MongoengineDbSingleton
from wiederverwendbar.starlette_admin import ActionLogAdmin, ActionLogger, FormCommand

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

# connect to database
MongoengineDbSingleton(init=True)

# create kombu connection
kombu_connection = Connection(MongoengineDbSingleton().connection_string)


# Create starlette app
app = Starlette(
    routes=[
        Route(
            "/",
            lambda r: HTMLResponse("<a href=/admin/>Click me to get to Admin!</a>"),
        ),
    ],
)


class MyAdmin(Admin, ActionLogAdmin):
    ...


# Create admin
admin = MyAdmin(title="Test Admin", kombu_connection=kombu_connection)


class Test(Document):
    meta = {"collection": "test"}

    test_str = StringField()


class TestView(ModelView):
    def __init__(self):
        super().__init__(document=Test, icon="fa fa-server", name="Test", label="Test")

    actions = ["delete", "test_action_normal", "test_action_action_log"]

    @action(name="test_action_normal",
            text="Test Action - Normal")
    # confirmation="Möchtest du die Test Aktion durchführen?",
    # icon_class="fa-regular fa-network-wired",
    # submit_btn_text="Ja, fortsetzen",
    # submit_btn_class="btn-success")
    async def test_action_normal(self, request: Request, pk: list[str]) -> str:
        await asyncio.sleep(2)

        return "Test Aktion erfolgreich."

    @action(name="test_action_action_log",
            text="Test Action - Action Log")
    # confirmation="Möchtest du die Test Aktion durchführen?",
    # icon_class="fa-regular fa-network-wired",
    # submit_btn_text="Ja, fortsetzen",
    # submit_btn_class="btn-success")
    async def test_action_action_log(self, request: Request, pk: list[str]) -> str:
        with await ActionLogger(request, parent=logger) as action_logger:
            # send form
            action_logger_form_data = FormCommand(action_logger,
                                                  """<form>
                      <div class="mt-3">
                          <input type="hidden" name="hidden">
                          <div>
                              <label class="form-check">
                                  <input type="radio" class="form-check-input" name="action" value="choice1" checked>
                                  <span class="form-check-label">Choice 1</span>
                              </label>
                              <label class="form-check">
                                  <input type="radio" class="form-check-input" name="action" value="choice2">
                                  <span class="form-check-label">Choice 2</span>
                              </label>
                              <label class="form-check">
                                  <input type="radio" class="form-check-input" name="action" value="choice3">
                                  <span class="form-check-label">Choice 3</span>
                              </label>
                          </div>
                      </div>
                  </form>""",
                                                  "Weiter",
                                                  "Abbrechen")()
            if not action_logger_form_data:
                raise ActionFailed("Test Aktion abgebrochen.")

            action_logger_yes_no = action_logger.yes_no("Möchtest du fortfahren?")()
            if not action_logger_yes_no:
                raise ActionFailed("Test Aktion abgebrochen.")

            # use context manager to ensure that the logger is finalized
            with action_logger.sub_logger("sub_action_1", "Sub Action 1", steps=3, ignore_loggers_like=["pymongo"]) as sub_logger:
                sub_logger.info("Test Aktion startet ...")
                sub_logger.debug("Debug")
                sub_logger.info("Test Aktion step 1")
                await asyncio.sleep(2)
                sub_logger.next_step()
                sub_logger.info("Test Aktion step 2")

                # send form with positive/negative buttons
                sub_logger_confirm = sub_logger.confirm("Information")()
                sub_logger.info(f"Confirm: {sub_logger_confirm}")


                sub_logger_yes_no = sub_logger.yes_no("Möchtest du fortfahren?")()
                if not sub_logger_yes_no:
                    sub_logger.finalize(success=False, on_error_msg="Test Aktion abgebrochen.")

                await asyncio.sleep(2)
                sub_logger.next_step()
                sub_logger.steps += 100
                for i in range(1, 100):
                    sub_logger.info(f"Test Aktion step 2 - {i}")
                    sub_logger.next_step()
                    await asyncio.sleep(0.01)
                sub_logger.info("Test Aktion step 3")
                await asyncio.sleep(2)

        return "Test Aktion erfolgreich."


# Add views to admin#
admin.add_view(TestView())

# Mount admin to app
admin.mount_to(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
