# -*- coding: utf-8 -*-
"""
Generate QR Code signed PDF with private GPG key

TODO:
- First line of message missing in signature!

@author: Dominik Schürmann
"""

import qrencode # functions: encode, encode_scaled

import os

import gnupg

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.platypus.flowables import Image, HRFlowable, ParagraphAndImage, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.frames import Frame
from reportlab.lib.units import inch
from reportlab.rl_config import defaultPageSize
PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()

# gpg config
verbose = False
use_agent = True # if not using gpg agent define passphrase below
passphrase = ""
keyid = None # define keyid, run program to see valid key ids, None means using default

# document
title = "QR Code Signed Document"
message = """Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
sed diam nonumy eirmod tempor invidunt ut labore et dolore magna
aliquyam erat, sed diam voluptua. At vero eos et accusam et justo
duo dolores et ea rebum. Stet clita kasd gubergren, no sea
takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum
dolor sit amet, consetetur sadipscing elitr, sed diam nonumy
eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
sed diam voluptua. At vero eos et accusam et justo duo dolores
et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus
est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet,
consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt
ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero
eos et accusam et justo duo dolores et ea rebum. Stet clita kasd
gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."""



def myFirstPage(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Bold', 16)
    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, title)
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, "Page %d - %s" % (doc.page, title))


    frame_width = PAGE_WIDTH-200
    hr = HRFlowable()
    space = Spacer(frame_width, 20)
    style = styles["Normal"]
    qr_info = """<para rightIndent=10 leftIndent=20 alignment=right>This document is signed with the QR-Code shown on the right. Validate it using a Scanner App."""
    par = Paragraph(qr_info, style)
    im = Image("qrcode.png", 101, 101)
    pandi = ParagraphAndImage(par, im, xpad=3, ypad=30, side='right')
    
    frame = Frame(100, 0, frame_width, 200, showBoundary=1)
    frame.add(hr, canvas)
    frame.add(space, canvas)
    frame.add(pandi, canvas)
    canvas.restoreState()
    
def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "Page %d - %s" % (doc.page, title))
    canvas.restoreState()


def generate_pdf(message, signed_message):
    doc = SimpleDocTemplate("qr_code_signed.pdf")
    Story = [Spacer(1,2*inch)]
    style = styles["Normal"]
    p = Paragraph(message, style)
    Story.append(p)
    Story.append(Spacer(1,200)) #0.2*inch
    
    # generate and save qrcode
    qrcode_version, qrcode_size, qrcode_im = qrencode.encode(
                                            signed_message, version=0, level=0,
                                            hint=qrencode.QR_MODE_8,
                                            case_sensitive=True)                
    qrcode_im.save("qrcode.png", "PNG")
    
    doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
    
    
def gpg_sign(message):
    homedir = os.path.expanduser('~')
    gpgdir = os.path.join(homedir, '.gnupg') # linux specific?
    if not os.path.exists(gpgdir) or not os.path.isdir(gpgdir):
        print "GPG directory does not exist or is not a directory: %s" % gpgdir
    else:
        gpg = gnupg.GPG(gnupghome=gpgdir, gpgbinary='gpg', verbose=verbose, use_agent=use_agent)
        print "Successfully set of GPG directory: %s" % gpgdir
    
    private_keys = gpg.list_keys(True) # True => private keys
    
    print("valid keys with key id and emails:")
    for key in private_keys:
        print("----------------------------------")
        print("key id: "+str(key['keyid']))
        for uid in key['uids']:
            print(uid)
    
    signed_data = gpg.sign(message, keyid=keyid, passphrase=passphrase, clearsign=True)
    return str(signed_data)
        

signed_message = gpg_sign(message)
generate_pdf(message, signed_message)

print("\n\n\n ")
print(str(message))
print(str(signed_message))