import git
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from keys import mailpass
#
# used for errors and notification
#
def sendmail(description):
  mail_content = f"anmonitor: Hello, there is a new release: \n {description}"

  #The mail addresses and password
  sender_address = 'am@kandek.com'
  receiver_address = 'wolfgang@kandek.com'
  #Setup the MIME
  message = MIMEMultipart()
  message['From'] = sender_address
  message['To'] = receiver_address
  message['Subject'] = 'New anmonitor release'   #The subject line
  #The body and the attachments for the mail
  message.attach(MIMEText(mail_content, 'plain'))
  #Create SMTP session for sending the mail
  session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
  session.starttls() #enable security
  session.login(sender_address, mailpass) #login with mail_id and password
  text = message.as_string()
  session.sendmail(sender_address, receiver_address, text)
  session.quit()
  print("Mail Sent")


repo = "gitopsrepo"
pattern = "README.md"
notification = ""

# set the repo to use
repo = git.Repo('.')

# what are the release available
newtag = {} 
taginfo = repo.git.ls_remote("--tags")
for rt in taginfo.split("\n"):
  rte = rt.split("/") 
  rt = rte[len(rte)-1] 
  newtag[rt] = 1
sortedtags = dict(sorted(newtag.items()))
latest = list(sortedtags)[-1]

# which ones do we have locally 
for lt in repo.tags:
  for rt in newtag:
    if str(lt) in rt:
      newtag[rt] = 0

# is there a new release
newrelease = 0
for t in newtag:
  print(t, newtag[t])
  newrelease = newrelease + newtag[t]

# what is the checkout value
status = repo.git.status()
for s in status.split("\n"):
  if "HEAD detached" in s:
    se = s.split();
    verco = se[len(se)-1]
    print(verco)

# if there is a new release
if newrelease > 0:
  # update local repo
  repo.git.fetch()

# in any case  check if we can go to a newer version
print(verco, latest)
if verco != latest:
  print("in != branch")
  # get logs
  loginfo = repo.git.log('-p', 'HEAD..origin/main')

  # look at the diff
  checkfile = False
  newlines = 0
  dellines = 0
  for logline in loginfo.split("\n"):
    if "diff" in logline:
      # get last element, then eliminate the lead 2 characters - typically "b/"
      le = logline.split()
      filename = le[len(le)-1]
      filename = filename[2:]
      if pattern in filename:
        print(filename)
        print("  ", logline)
        notification = notification + logline + "\n"
        checkfile = True
      else:
        checkfile = False
    if len(logline) > 1 and checkfile:
      notification = notification + logline + "\n"
      print(logline)
      if "+" == logline[0] and "+" != logline[1]:
        # line added
        newlines = newlines + 1
      if "-" == logline[0] and "-" != logline[1]:
        # line removed
        dellines = dellines + 1
    
#  if "Date:" in logline:
#    print(logline)
#  if "@@" in logline:
#    print(logline)

  if newlines > 0 or dellines > 0:
    notification = notification + f"Moving to {latest}" + "\n"
    notification = notification + f"  updated {newlines} {dellines}"
    repo.git.checkout(latest)
    sendmail(notification)
else:
  print("no new release")
