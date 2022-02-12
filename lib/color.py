
#ANSI COLORS FOR XTERM
CRES=chr(27)+"[0m"
CBOLD=chr(27)+"[1m"
CBLACK=chr(27)+"[38;5;0m"
CRED=chr(27)+"[38;5;1m"
CGRN=chr(27)+"[38;5;2m"
CYELLO=chr(27)+"[38;5;3m"
CBLUE=chr(27)+"[38;5;4m"
CMAG=chr(27)+"[38;5;5m"
CCYAN=chr(27)+"[38;5;6m"
CWHITE=chr(27)+"[38;5;7m"
CBBLACK=chr(27)+"[38;5;8m"
CBRED=chr(27)+"[38;5;9m"
CBGRN=chr(27)+"[38;5;10m"
CBYELLO=chr(27)+"[38;5;11m"
CBBLUE=chr(27)+"[38;5;12m"
CBMAG=chr(27)+"[38;5;13m"
CBCYAN=chr(27)+"[38;5;14m"
CBWHITE=chr(27)+"[38;5;15m"
#END OF COLORS

def mcolor(col,msg,ucolo=None):
    #Leaving the default color as it is.
    if col=="default": return msg
    if ucolo==True:
        #We are checking user settings.
        return col+msg+CRES
    elif ucolo==False:
        return msg
    elif ucolo==None:
        #User settings is not our business.
        return col+msg+CRES
    else:
        return msg


#ANSI COLORS FOR WEBSOCKET
#probably should be parsed by the client from xterm colors
#As I have no means of testing the websocket stuff, I'll leave it for now.
hCRES="</p>"
hCBOLD="<p style='weight:bold'>"
hCBLACK="<p style='color:black'>"
hCRED="<p style='color:red'>"
hCGRN="<p style='color:green'>"
hCYELLO="<p style='color:yellow'>"
hCBLUE="<p style='color:blue'>"
hCMAG="<p style='color:magenta'>"
hCCYAN="<p style='color:cyan'>"
hCWHITE="<p style='color:white'>"
hCBBLACK="<p style='color:black'>"
hCBRED="<p style='color:red'>"
hCBGRN="<p style='color:green'>"
hCBYELLO="<p style='color:yellow'>"
hCBBLUE="<p style='color:blue'>"
hCBMAG="<p style='color:magenta'>"
hCBCYAN="<p style='color:cyan'>"
hCBWHITE="<p style='color:white'>"
#END OF COLORS
