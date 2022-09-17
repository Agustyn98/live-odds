from avro.io import DatumWriter
import avro
import io
import json
from google.api_core.exceptions import NotFound
from google.cloud.pubsub import PublisherClient
from google.pubsub_v1.types import Encoding


project_id = "marine-bison-360321"
topic_id = "match_bets2"
avsc_file = "schema_avro.json"

def publish(record):
    publisher_client = PublisherClient()
    topic_path = publisher_client.topic_path(project_id, topic_id)

    # Prepare to write Avro records to the binary output stream.
    avro_schema = avro.schema.parse(open(avsc_file, "rb").read())
    writer = DatumWriter(avro_schema)
    bout = io.BytesIO()

    try:
        # Get the topic encoding type.
        topic = publisher_client.get_topic(request={"topic": topic_path})
        encoding = topic.schema_settings.encoding

        # Encode the data
        if encoding == Encoding.JSON:
            data_str = json.dumps(record)
            data = data_str.encode("utf-8")
        else:
            print(f"No encoding specified in {topic_path}. Abort.")
            exit(0)

        future = publisher_client.publish(topic_path, data)
        print(f"Published message ID: {future.result()}")

    except NotFound:
        print(f"{topic_id} not found.")
