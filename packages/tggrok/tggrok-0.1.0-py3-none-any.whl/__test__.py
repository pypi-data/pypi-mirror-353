from tggrok import Grok


grok: Grok = Grok(
    api_id='25652634',
    api_hash='20f4d4d7d5b58b89e9e9e52efe5c728a',
    phone_number='+79267228933',
    workdir='src',
)


response: str = grok.ask('Hi there')
print(response)
grok.reset_dialog()
