# Starting the Telegram bot for testing

```
LOGLEVEL=DEBUG python3 main.py <test-token> <group-id>
```

- `test-token`: follow https://core.telegram.org/bots#6-botfather to create a bot for testing, and note down the token
- `group-id`: the id of the chat room to which the bot should broadcast message related to its status; in testing this would normally be your own chat with the bot. Follow https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id to get the relevant group id
