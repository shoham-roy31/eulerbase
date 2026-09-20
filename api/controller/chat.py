import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from ..models import (
    ChatRequest,
    ChatResponse,
    HTTPError
)
from utils import (
    GraphDB,
    graphRAG,
    load_conf
)
load_dotenv()
CHAT_CONF_PATH = Path(__file__).resolve().parent / "conf" / "chat.conf"
URI = os.environ["URI"]
username = os.environ["USERNAME"]
password = os.environ["password"]
defualt_db = os.environ["DEFAULT_DB"]
config = load_conf(CHAT_CONF_PATH)
print(config)

db = GraphDB(
    URI = URI,
    AUTH = (username,password)
)
kB = graphRAG(
    llm = config["llm"],
    embedding_model = config["embedding_model"],
    index_name = "dataProductIndex",
    driver = db
)

async def generate(req:ChatRequest) -> ChatResponse | HTTPError:
    print(f"Chat History: {kB.history.messages}")
    return ChatResponse(response = kB.search(req.context),
                        token_generate_time = datetime.now().isoformat(),
                        metadata = req
                        )

