import re



txt = r'abc,def"'
p = re.compile('^([^,])*')
m = p.search(txt)

print (m)


