import asyncio
import json
import logging
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Dict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from browser_use import Agent, Browser
from browser_use.agent.service import set_current_session
from browser_use.browser.context import BrowserContextConfig
from browser_use.browser.context import BrowserContext

load_dotenv()
logging.basicConfig(level=logging.INFO)
session_agents: Dict[str, Agent] = {}


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def start_agent_async(self, session_id: str, task: str, context: str):
        browser = Browser()
        llm = ChatOpenAI(model='gpt-4o')
        planner_llm = ChatOpenAI(model='o3-mini')
        
        browserConfig = BrowserContextConfig(
            highlight_elements=False,
        )
        
        browser = Browser()
        browserCcontext = BrowserContext(browser=browser, config=browserConfig)

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            browser_context=browserCcontext,
            message_context=context,
            enable_memory=False,
            planner_llm=planner_llm,
            use_vision_for_planner=False,
            planner_interval=3,
            use_vision=True,
        )
        session_agents[session_id] = agent
        set_current_session(session_id)
        logging.info(f"Agent iniciado com session_id={session_id}, task={task}")
        Thread(target=self.start_agent_sync, args=(agent, session_id)).start()

    def start_agent_sync(self, agent: Agent, session_id: str):
        from browser_use.agent.service import set_current_session
        set_current_session(session_id)
        result = asyncio.run(agent.run())
        # logging.info('\n \n 🔴🔴🔴🔴 result: ' + str(result.status))

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
                session_id = request_json.get('session_id')

                if not task:
                    raise ValueError("Missing task parameter")

                # inicia o agent usando o mesmo session_id vindo do React
                self.start_agent_async(session_id, task, context)

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
            if agent.browser:
                # logging.info('🔴🔴🔴🔴 agent.browser')
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
