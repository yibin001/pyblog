import akismet

akismet.USERAGENT = "yibinim/1.0"

my_api_key = "d74e529c1972"

try:
    real_key = akismet.verify_key(my_api_key,"http://yibinim.sinaapp.com")
    if real_key:
        is_spam = akismet.comment_check(my_api_key,"http://yibinim.sinaapp.com",
            "127.0.0.1", "Mozilla/5.0 (...) Gecko/20051111 Firefox/1.5",
            comment_content="dear author,hello,this is you coat")
        if is_spam:
            print "Yup, that's spam alright."
        else:
            print "Hooray, your users aren't scum!"
except akismet.AkismetError, e:
    print e.response, e.statuscode

# If you're a good person, you can report false positives via akismet.submit_ham(),
# and false negatives via akismet.submit_spam(), using exactly the same parameters
# as akismet.comment_check.