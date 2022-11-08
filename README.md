# Deployment

Deployment is fairly straightforward. It's recommended to deploy this as a systemd service on a compatible Linux distro.

1. Get the source code. On your server, clone the repo using git
2. Make sure python3 & pip3 have been installed. Then install the dependencies for the project

  ```
  pip3 install $(cat requirements.txt)
  ```
3. Copy [systemd template service file](etc/systemd/telegram-gmgl.service) to your systemd service directory. Normally this would be `/etc/systemd/system/`. NOTE THIS FILE IS ONLY A TEMPLATE! Make sure you understand its content and substitute the stubs with actual auth details.
4. Obtain the auth details from the project maintainer via a secure channel and put them into the service file
5. Start the service and notify ngocn group members. Try a few commands (e.g., `/help`) to see if everything works. `systemctl enable telegram-gmgl` as necessary.

Since your server will be holding the auth details, make sure it's secured and checked periodically.

# Development

Development on this project uses standard pull request workflow i.e., you work on your own fork and then make a pull request. If you want to become a maintainer, you need to contact the current maintainer and let he add you into the project.

Always run tests for small or big changes. For big changes, it's recommended to use your own Telegram bot instance (see second section below).

*Note tests are automatically run in Github Action on pull requests & pushes.*

## Tests

```
python3 test.py
```

This tests a couple things:

- text processing, including auto-formatting
- generation of correct images given set input
- converting markdown input into plaintext (for putting into img)

All testsets are within [test/](test/). The test runs by trying to match the program output with the correct output files (golden output) inside that dir.

**This means when you have made a change that affects the golden output, you will need to update the golden output checked into the repo.** You can do this by using the command below:

```
python3 test.py gen
```

This will *override the golden output with your current program output for each and every input in the testsets, including images and text*.

Before doing this though, you probably want to make sure your change is correct. You can do this by adding some tests of your own - put the input and output files in the test hierarchy and make sure those pass first. Then - after you run the command above to generate the new golden output - **review all the changes in those golden output and check that they look okay.**

## Use your own Telegram bot for testing

This would be useful when you want to add new features and test them out on Telegram without interfering with the existing (deployed) bot instance. The guide below outlines the steeps needed to use a test bot that's only visible to yourself on Telegram.

1. Follow https://core.telegram.org/bots#6-botfather to create a bot for testing, and note down the token.
2. In Telegram create a new chat room with your own bot - this will be the place where you test your bot commands and receive broadcast messages from it. You will need the id for this chat. Follow https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id to get its group id.
3. Since the GMGL bot also automatically posts generated news to a channel, you will also need to create a test channel for this. Once you have it, note down its channel id i.e., for `@xyz` that would be `xyz`
4. Now you can spin up your test GMGL instance by using the command below

  ```
  DEBUGONLY=1 LOGLEVEL=DEBUG python3 main.py <test-token> <group-id> NO-GITLAB <channel-id>
  ```
  
  with `test-token` from step 1, `group-id` from step 2, `channel-id` from step 3.
  
  Note `NO-GITLAB` is a stub for gitlab token - you don't want to publish to Gitlab for this, so anything works fine here. `DEBUGONLY=1` is important as it disables Gitlab publishing.
