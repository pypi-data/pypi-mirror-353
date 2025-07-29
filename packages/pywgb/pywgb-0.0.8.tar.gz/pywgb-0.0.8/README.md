# pywgb
Wecom(A.K.A. WeChat Work) Group Bot python API.

## Homepage

> [ChowRex/pywgb: Wecom(A.K.A Wechat Work) Group Bot python API.](https://github.com/ChowRex/pywgb)

## How to use

1. Create a [Wecom Group Bot](https://qinglian.tencent.com/help/docs/2YhR-6/).

2. Copy the webhook URL or just the `key`. It **MUST** contains an [UUID (8-4-4-4-12)](https://en.wikipedia.org/wiki/Universally_unique_identifier), like:

   - `Webhook`: *https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=UUID*
   - `Key`: *UUID*

3. Install this package: 

    ```bash
    # Normally use this if you won't send voice message
    pip install -U pywgb
    # You can install full version by this
    pip install -U "pywgb[all]"
    ```

4. If you want to send simple messages, refer code below:

   ```python
   from pywgb import TextWeComGroupBot, MarkdownWeComGroupBot, ImageWeComGroupBot, NewsWeComGroupBot, FileWeComGroupBot, VoiceWeComGroupBot
   
   KEY = "PASTE_YOUR_KEY_OR_WEBHOOKURL_HERE"
   
   # If you want to send Text message, use this.
   msg = "This is a test Text message."
   bot = TextWeComGroupBot(KEY)
   bot.send(msg)
   
   # If you want to send Markdown message, use this.
   bot = MarkdownWeComGroupBot(KEY)
   col = [bot.green, bot.gray, bot.orange]
   msg = [col[idx % 3](ltr) for idx, ltr in enumerate("colorful")]
   msg = f"This is a {''.join(msg)} Markdown message"
   bot.send(msg)
   
   # If you want to send Image message, use this.
   file = "Path/To/Your/Image.png" or "Path/To/Your/Image.jpg"
   bot = ImageWeComGroupBot(KEY)
   bot.send(file_path=file)
   
   # If you want to send News message, use this.
   articles = [
       {
           "title": "This is a test news",
           "description": "You can add description here",
           "url": "www.tencent.com",
           # Here is the link of picture
           "picurl": "https://www.tencent.com/img/index/tencent_logo.png"
       },
   ]
   bot = NewsWeComGroupBot(KEY)
   bot.send(articles=articles)
   
   # If you want to send File message, use this.
   file = "Path/To/Your/File.suffix"
   bot = FileWeComGroupBot(KEY)
   bot.send(file_path=file)
   
   # If you want to send Voice message, use this.
   file = "Path/To/Your/Voice.amr"  # BE ADVISED: ONLY support amr file
   bot = VoiceWeComGroupBot(KEY)
   bot.send(file_path=file)
   
   ```

5. Send template card messages (***Advanced usage***)

    ```python
    from pywgb import TextCardWeComGroupBot, NewsCardWeComGroupBot
    
    KEY = "PASTE_YOUR_KEY_OR_WEBHOOKURL_HERE"
    
    # Prepare the text card content
    kwargs = {
        "main_title": {
            "title": "Test message",
            "desc": "This is a test template text card message"
        },
        "emphasis_content": {
            "title": "100",
            "desc": "No meaning"
        },
        "quote_area": {
            "type": 1,
            "url": "https://work.weixin.qq.com/?from=openApi",
            "title": "Title reference",
            "quote_text": "Hello\nWorld!"
        },
        "sub_title_text": "This is sub-title",
        "horizontal_content_list": [{
            "keyname": "Author",
            "value": "Rex"
        }, {
            "keyname": "Google",
            "value": "Click to go",
            "type": 1,
            "url": "https://google.com"
        }],
        "jump_list": [{
            "type": 1,
            "url": "https://bing.com",
            "title": "Bing"
        }],
        "card_action": {
            "type": 1,
            "url": "https://work.weixin.qq.com/?from=openApi",
        }
    }
    bot = TextCardWeComGroupBot(KEY)
    bot.send(**kwargs)
    
    # Prepare the news card content
    kwargs = {
        "source": {
            "icon_url":
                "https://wework.qpic.cn/wwpic/252813_jOfDHtcISzuodLa_1629280209/0",
            "desc":
                "This is for testing",
            "desc_color":
                0
        },
        "main_title": {
            "title": "Test message",
            "desc": "This is a test template news card message"
        },
        "card_image": {
            "url":
                "https://wework.qpic.cn/wwpic/354393_4zpkKXd7SrGMvfg_1629280616/0",
            "aspect_ratio":
                2.25
        },
        "image_text_area": {
            "type":
                1,
            "url":
                "https://work.weixin.qq.com",
            "title":
                "Welcom to use pywgb",
            "desc":
                "This is a test message",
            "image_url":
                "https://wework.qpic.cn/wwpic/354393_4zpkKXd7SrGMvfg_1629280616/0"
        },
        "quote_area": {
            "type": 1,
            "url": "https://work.weixin.qq.com/?from=openApi",
            "title": "Title reference",
            "quote_text": "Hello\nWorld!"
        },
        "vertical_content_list": [{
            "title": "Hi, there",
            "desc": "Welcome to use"
        }],
        "horizontal_content_list": [{
            "keyname": "Author",
            "value": "Rex"
        }, {
            "keyname": "Google",
            "value": "Click to go",
            "type": 1,
            "url": "https://google.com"
        }],
        "jump_list": [{
            "type": 1,
            "url": "https://bing.com",
            "title": "Bing"
        }],
        "card_action": {
            "type": 1,
            "url": "https://work.weixin.qq.com/?from=openApi",
        }
    }
    bot = NewsCardWeComGroupBot(KEY)
    bot.send(**kwargs)
    
    ```

## Official Docs

> **Only Chinese** doc: [群机器人配置说明 - 文档 - 企业微信开发者中心](https://developer.work.weixin.qq.com/document/path/99110)

## Roadmap

- [x] v0.0.1: 🎉 Initial project. Offering send `Text` and `Markdown` type message.
- [x] v0.0.2: 🖼️ Add `Image` type message support;

  - Add overheat detect function and unified exception handling
- [x] v0.0.3: 📰 Add `News` type message support;

  - Move bots into a new module: `bot`
- [x] v0.0.4: 📂 Add `File` type message support;

    - Refactor `bot` module
- [x] v0.0.5: 🗣️ Add `Voice` type message support.
    - Refactor `deco` module
    - Add `verify_file` decorator
    - Introverted parameters check errors
    - Add more content into README.md
- [x] v0.0.6: 🩹 Add `Voice` and `File` type size check.
- [x] v0.0.7: 🗒️ Add `TextCard` type message support.
- [x] v0.0.8: 🗃️ Add `NewsCard` type message support.
- [ ] v1.0.0: 👍 First FULL capacity stable version release.Fix bugs and so on.

