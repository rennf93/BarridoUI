import datetime
import pandas
from risk.models import Score
from barridoUI.celery import app
from celery.utils.log import get_task_logger
from django.core.files.base import ContentFile
from risk.engine_client import EngineClient

logger = get_task_logger(__name__)


@app.task()
def generate_score_task(score_id):
    score = Score.objects.get(id=score_id)
    score.status = "processing"
    score.save()
    engine_client = EngineClient()
    data_csv = pandas.read_csv(score.data.path, delimiter=";")
    scores = list()
    for index, value in data_csv.iterrows():
        response = engine_client.score(score.policy, score.workflow, value.to_dict())
        if response.status_code == 200:
            scores.append(response.json().get("variables"))
    scores_csv = pandas.DataFrame(scores).to_csv(quotechar='"', sep=";", encoding='utf-8')
    score.result.save("scoring-{}.csv".format(datetime.datetime.now().strftime("%Y%m%d%H%M%s")),
                      ContentFile(scores_csv))
    score.status = "finished"
    score.save()
