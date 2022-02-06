import smtplib
import feedparser
from email.mime.text import MIMEText
from email.header import Header

# 관심 RSS feed 주소를 추가, 변경한다.
rss_feeds = [
    'http://file.mk.co.kr/news/rss/rss_30100041.xml',
    'http://file.mk.co.kr/news/rss/rss_50300009.xml'
]

# words of interest. 관심 단어
WOI = ['금리', '대출', '가격', '리스크']

out = []
for feed in rss_feeds:
    d = feedparser.parse(feed)
    for entry in d.entries:
        for w in WOI:  # 관심 단어가 제목이나 요약에 있는지 살핀다
            if w in entry['title'] or w in entry['summary']:
                s = '* {} {}'.format(entry['title'], entry['link'])
                out.append(s)
                break
message = '\n'.join(out)

if message:
    # 메일 발송
    subject = 'RSS News'
    mail_from = mail_to = 'hanhonghee@gmail.com'
    id_ = 'hanhonghee@gmail.com'
    pw_ = 'h!an19845'

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(id_, pw_)

    msg = MIMEText(message.encode('utf-8'), _subtype='plain', _charset='utf-8')
    msg['Subject'] = Header(subject.encode('utf-8'), 'utf-8')
    msg['From'] = mail_from
    msg['To'] = mail_to

    smtp.sendmail(mail_from, mail_to, msg.as_string())
    smtp.quit()