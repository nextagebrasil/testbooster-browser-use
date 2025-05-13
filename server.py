import json
import logging
import asyncio

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from uuid import uuid4
from typing import Dict
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser
from dotenv import load_dotenv
from threading import Thread
from browser_use.agent.service import set_current_session


load_dotenv()
logging.basicConfig(level=logging.INFO)
session_agents: Dict[str, Agent] = {}

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def start_agent_async(self, task: str, context: str):
        session_id = str(uuid4())
        browser = Browser()

        llm = ChatOpenAI(model='gpt-4o')
        planner_llm = ChatOpenAI(model='o3-mini')

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            message_context=context,
            enable_memory=False,
            planner_llm=planner_llm,  # Separate model for planning
            use_vision_for_planner=False,  # Disable vision for planner
            planner_interval=3,  # Plan every 4 steps
            use_vision=True,
        )
        session_agents[session_id] = agent
        set_current_session(session_id)
        logging.info(f"Agent iniciado com session_id={session_id}, task={task}")
        t1 = Thread(target=self.start_agent_sync, args=(agent,))
        t1.start()
        return session_id

    def start_agent_sync(self, agent: Agent):
        result = asyncio.run(agent.run())

    def do_POST(self):
        if self.path == '/start-agent/':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            logger.addHandler(handler)
            try:
                request_json = json.loads(post_data)
                task = request_json.get('task')
                context = request_json.get('context')

                if not task:
                    raise ValueError("Missing task parameter")

                session_id = self.start_agent_async(task, context) # Não esperando result

                response_data = {
                    "status": "success",
                    "session_id": session_id,
                    "result": "result"
                }
                self._set_headers(200)

            except Exception as e:
                logging.error(f"Erro ao processar POST /start-agent/: {str(e)}")
                response_data = {"status": "error", "detail": str(e)}
                self._set_headers(500)

            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"detail": "Endpoint not found"}).encode('utf-8'))

    def do_DELETE(self):
        if self.path.startswith('/end-agent/'):
            session_id = self.path.split('/')[-1]  # extrair session_id da URL
            agent = session_agents.pop(session_id, None)

            if not agent:
                self._set_headers(404)
                response_data = {"status": "error", "detail": "Session not found"}
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                return

            # Caso exista método para encerrar o browser, utilize:
            # Exemplo seguro:
            if hasattr(agent.browser, 'close') and callable(agent.browser.close):
                agent.browser.close()
                agent.pause()
                agent.close()

            logging.info(f"Agent terminado session_id={session_id}")

            self._set_headers(200)
            response_data = {"status": "ended", "session_id": session_id}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"detail": "Endpoint not found"}).encode('utf-8'))


def run(server_class=ThreadingHTTPServer, handler_class=SimpleHTTPRequestHandler, port=9090):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Servidor HTTP iniciado na porta {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Servidor HTTP encerrado manualmente.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run()