import chainlit as cl
from agent import run_agent

@cl.on_chat_start
async def start():
    await cl.Message(content="Smart AI Agent ready. CryptoMentions & business tools enabled.").send()

@cl.on_message
async def main(message: cl.Message):
    thread_id = cl.context.session.id
    response = run_agent(message.content, thread_id=thread_id)
    await cl.Message(content=response).send()
