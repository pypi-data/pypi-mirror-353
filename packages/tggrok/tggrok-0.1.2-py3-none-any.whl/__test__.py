from tggrok import Grok


grok: Grok = Grok(
    api_id='25652634',
    api_hash='20f4d4d7d5b58b89e9e9e52efe5c728a',
    phone_number='+79267228933',
    workdir='src',
)


response: int = grok.ask(
    prompt='What is 17 + 22?\nRespond with a number and nothing else',
    process=lambda x: int(x),
    mark_as_read=True,
    keep_context=False,
)
print(response)
