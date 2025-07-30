# No-Profanity
**No-Profanity** is a simple library that uses regexes to detect and block profanity in strings. It's designed to detect even the most creative modifications of profanity.

## How to use?
The library contains 1 class. This class contains 5 functions.

```py
from no_profanity import ProfanityFilter

# ProfanityFilter(censor_symbol: str = "*")
filter = ProfanityFilter()

# add_custom_words(words: list) -> None
filter.add_custom_words(["happy", "hello"])

# add_custom_wordlist(filepath: str) -> None
filter.add_custom_wordlist("./wordlist.txt")

# set_censor_symbol(censor_symbol: str) -> None
filter.set_censor_symbol("-")

# is_profanity(txt: str) -> bool
filter.is_profanity("my name is Lime") # False
filter.is_profanity("shut the fuck up") # True

# censor_text(txt: str, censor_symbol: str = None) -> str
filter.censor_text("what the fuck is this") # Output: what the ---- is this

# Without set_censor_symbol(): what the **** is this

# full_detection(txt: str) -> list[dict]
# [
#   {
#       string_match,
#       start,
#       end,
#       found_word
#   }, ...
# ]

filter.full_detection("you fuck1ng bitch") # [{'string_match': 'fuck1ng', 'start': 4, 'end': 11, 'found_word': 'fucking'}, {'string_match': 'bitch', 'start': 12, 'end': 17, 'found_word': 'bitch'}]
```

## Pros
The library can detect *modified* profanity. Examples:
```py
filter.is_profanity("fuckfuck") # True
filter.is_profanity("niggafuck") # True
filter.is_profanity("b i t c h") # True
filter.is_profanity("sexx") # True

filter.is_profanity("n1@@a") # True
filter.is_profanity("f u cckbitch es") # True

filter.is_profanity("@fuck@") # True
```

## Cons
The filter can be bypassed by putting an extra letter(s) that isn't part of profanity. This will be fixed in the future! :D
```py
filter.is_profanity("afuck") # False
```

This library has originally been made for my Discord bot **AutoProtection**, but now it's released for everyone to use!
If you have more questions, please contact me on my [Discord server](https://discord.com/invite/tr55DGHEwN).

Thank you for reading this! I hope you'll like my first library. I'm always opened to new ideas for improvements! ^^
