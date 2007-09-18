# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import datetime
import time
from report.interface import report_rml
from report.interface import toxml
import pooler
from osv import osv,orm
from time import strptime

from xml.dom import minidom

import sys
import os
import re
import netsvc
import base64
import wizard
import photo_shadow

def escape(s):
	return str(s or '').replace('<br/>','').decode('latin1','replace').encode('utf-8')


class auction_catalog(report_rml):

	def create_xml(self, cr, uid, ids, data, context):

		xml = self.catalog_xml(cr, uid, ids, data, context)
		temp=self.post_process_xml_data(cr, uid, xml, context)

		return temp
	def catalog_xml(self,cr,uid,ids,data,context,cwid="0"):
		impl = minidom.getDOMImplementation()

		doc = impl.createDocument(None, "report", None)

		#catalog element
		catalog=doc.createElement('catalog')
		doc.documentElement.appendChild(catalog)


		infodb='info'
		commdb='comm'
		tab_avoid = []
		tab_no_photo=[]

		print "IDS::::::::::::::::",ids
		for id in ids:
			lot_ids=pooler.get_pool(cr.dbname).get('auction.lots').search(cr, uid, [('auction_id', '=', id)])
#			print "LOTSIDS",lot_ids
			ab=pooler.get_pool(cr.dbname).get('auction.lots').read(cr,uid,lot_ids,['auction_id','name','lot_num','lot_est1','lot_est2'],context)
		#abi=pooler.get_pool(cr.dbname).get('auction.lots').browse(cr,uid,ids)[0]
		#	print "AB::::::::::::::::",ab[0]['auction_id']
		#	print "AB::::::::::::::::",ab
		#print "AB::::::::::::::::",ab['auction_id'][0]
#		if not ab[0]['auction_id']:
#
#
#
##			raise wizard.except_wizard('UserError', 'There is no auctiondate for this lot!')
#			raise orm.except_orm('Error', 'There is no auction date for this lot!')
##			#raise Exception, 'ConceptionError, bad report name, should start with "report."'


			auction_dates_ids = [x["auction_id"][0] for x in ab]
			print "Auction_date_ids",auction_dates_ids

			res=pooler.get_pool(cr.dbname).get('auction.dates').read(cr,uid,ids,['name','auction1','auction2'],context)
		#res=self.read(cr,uid,ids,['name','auction1','auction2'],context)

		#for print a day of date
		#datetime.datetime(int(a[:4]),int(a[5:7]),int(a[8:])).strftime('%A')

			# name emelment
			key = 'name'
			categ = doc.createElement(key)
			categ.appendChild(doc.createTextNode(escape(res[0]["name"])))
			catalog.appendChild(categ)

			 #Auctuion Date element
			categ = doc.createElement("AuctionDate1")
			categ.appendChild(doc.createTextNode(escape(res[0]['auction1'])))
			catalog.appendChild(categ)

			# Action Date 2 element
			categ = doc.createElement("AuctionDate2")
			categ.appendChild(doc.createTextNode(escape(res[0]['auction2'])))
			catalog.appendChild(categ)



	#		  promotion element
			promo = doc.createElement('promotion1')

			fp = file('/home/nel/Desktop/images/lj8100.jpg','r')
			file_data = fp.read()



			promo.appendChild(doc.createTextNode(base64.encodestring(file_data)))
			catalog.appendChild(promo)

			promo = doc.createElement('promotion2')

			fp = file('/home/nel/Desktop/images/aeko_logo.jpg','r')
			file_data = fp.read()

			promo.appendChild(doc.createTextNode(base64.encodestring(file_data)))
			catalog.appendChild(promo)


			#product element
			products = doc.createElement('products')
			catalog.appendChild(products)

			side = 0
			length = 0
			auction_ids = []
			for test in ab:
				if test.has_key('auction_id'):
					auction_ids.append(str(test['auction_id'][0]))
			print 'query :select * from auction_lots where auction_id in ('+ ','.join(auction_ids)+')'
			print "auction",auction_ids
			cr.execute('select * from auction_lots where auction_id in ('+ ','.join(auction_ids)+')')
			res = cr.dictfetchall()
			for cat in res:
				print "CAT********",cat
				product =doc.createElement('product')
				products.appendChild(product)

				if cat['name']:
					infos = doc.createElement('infos')
					lines = re.split('<br/>|\n', cat['name'])

					for line in lines:
#						print  "LINE:::::::",line
						xline = doc.createElement('info')
						xline.appendChild(doc.createTextNode(escape(line)))
						infos.appendChild(xline)
					product.appendChild(infos)

					if cat['lot_num']:
						lnum = doc.createElement('lot_num')
						lnum.appendChild(doc.createTextNode(escape(cat['lot_num'])))
						infos.appendChild(lnum)

					dest = os.path.join('/tmp/pdf_catalog/',str(cwid),str(cat['obj_desc'])+'.jpg')
					if not cat['image']:
						print "Cat wiht no Image "
#						limg = doc.createElement('Image')
#						limg.appendChild(doc.createTextNode(cat['image']))
#						infos.appendChild(limg)


					else:
						if cat ['ref'] == 'medium':
							import random
							limg = doc.createElement('photo')
							file_name = '/tmp/image_%d.jpg' % (random.randint(1,1000),)
							fp = file(file_name,'wb+')
							content = base64.decodestring(cat['image'])
							fp.write(content)
							fp.close()
							fp = file(file_name,'r')
							size = photo_shadow.convert_catalog(fp, '/tmp/test.jpg')
							fp = file('/tmp/test.jpg')
							file_data = fp.read()
							test_data = base64.encodestring(file_data)
							limg.appendChild(doc.createTextNode(test_data))
							infos.appendChild(limg)

						elif cat ['ref'] == 'small':
							print"in else if"
							import random
							limg = doc.createElement('photo_small')
							file_name = '/tmp/image_%d.jpg' % (random.randint(1,1000),)
							fp = file(file_name,'wb+')
							content = base64.decodestring(cat['image'])
							fp.write(content)
							fp.close()
							fp = file(file_name,'r')
							size = photo_shadow.convert_catalog(fp, '/tmp/test.jpg',110)
							fp = file('/tmp/test.jpg')
							file_data = fp.read()
							test_data = base64.encodestring(file_data)

							limg.appendChild(doc.createTextNode(test_data))
							infos.appendChild(limg)


						else:
							print"in else if"
							import random
							limg = doc.createElement('photo_large')
							file_name = '/tmp/image_%d.jpg' % (random.randint(1,1000),)
							fp = file(file_name,'wb+')
							content = base64.decodestring(cat['image'])
							fp.write(content)
							fp.close()
							fp = file(file_name,'r')
							size = photo_shadow.convert_catalog(fp, '/tmp/test.jpg',220)
							fp = file('/tmp/test.jpg')
							file_data = fp.read()
							test_data = base64.encodestring(file_data)

							limg.appendChild(doc.createTextNode(test_data))
							infos.appendChild(limg)


				print "CAT>>>>>>>>>>>>>>>>>>",cat
				print "cat[ref]>>>>>>>>",cat['ref']


				for key in ('lot_est1','lot_est2'):

					ref2 = doc.createElement(key)
					ref2.appendChild(doc.createTextNode( escape(cat[key] or 0.0)))
					product.appendChild(ref2)

				oldlength = length
				length += 2.0


				if length>23.7:
					side += 1
					length = length - oldlength
					ref3 = doc.createElement('newpage')
					ref3.appendChild(doc.createTextNode( "1" ))
					product.appendChild(ref3)

				if side%2:
					ref4 = doc.createElement('side')
					ref4.appendChild(doc.createTextNode( "1" ))
					product.appendChild(ref4)

				xml1 = doc.toxml()
				print "xmllllllllllllllll",xml1

		return xml1
auction_catalog('report.auction.cat_flagy', 'auction.dates','','addons/auction/report/catalog2.xsl')

