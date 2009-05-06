# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import sys
#import arcgisscripting,
import datetime, os, zipfile, xml, string
from xml.dom.ext.reader.Sax2 import FromXmlStream
from xml.dom.ext import PrettyPrint

import urllib
import xml.dom.minidom
import pyexpat
#from xml.sax import ExpatParser

import wizard
import pooler
import tools
from osv import osv, fields


_earth_form =  '''<?xml version="1.0"?>
        <form string="Google Map/Earth" >
        <separator string="Enter Region(city/state/country)" colspan="4" />
        <newline/>
        <field name="region" help="wizard will create kml files using that kml file you can see the all partners which contains the given region for e.g if you enter India you can see all partners in india on google map within layer"/>
        </form> '''

_earth_fields = {
            'region': {'string': 'Region', 'type': 'char','required': True,},
            }

def geocode(address):
    # This function queries the Google Maps API geocoder with an
    # address. It gets back a csv file, which it then parses and
    # returns a string with the longitude and latitude of the address.

    # This isn't an actual maps key, you'll have to get one yourself.
    # Sign up for one here: http://code.google.com/apis/maps/signup.html
    mapsKey = 'abcdefgh'
    mapsUrl = 'http://maps.google.com/maps/geo?q='

    # This joins the parts of the URL together into one string.
    url = ''.join([mapsUrl,urllib.quote(address),'&output=csv&key=',mapsKey])

    # This retrieves the URL from Google.
    coordinates = urllib.urlopen(url).read().split(',')

    # This parses out the longitude and latitude, and then combines them into a string.
    coorText = '%s,%s' % (coordinates[3],coordinates[2])
    return coorText


def create_kml(self, cr, uid, data, context={}):
    # This function creates an XML document and adds the necessary
    # KML elements.

    address = ' '
    coordinates = []
    addresslist = []
    coordinates_text = ' '
    pool = pooler.get_pool(cr.dbname)
    partner_obj = pool.get('res.partner')
    path = tools.config['addons_path']
    fileName = path + '/google_earth/kml/partner_region.kml'
    address_obj= pool.get('res.partner.address')
    address_with_country_ids = address_obj.search(cr, uid, [('country_id.name','=', data['form']['region'])])
    address_with_state_ids = address_obj.search(cr, uid, [('state_id.name','=', data['form']['region'])])
    address_with_city_ids = address_obj.search(cr, uid, [('city','=', data['form']['region'])])

    partner_ids = partner_obj.search(cr, uid, [])
    partners = partner_obj.browse(cr, uid, partner_ids)
    country_list = []
    for part in partners:
        #Todo: should be check for contact/defualt type address
        if part.address and part.address[0].country_id and part.address[0].country_id.name:
            if not string.upper(part.address[0].country_id.name) in country_list:
                cntry = string.upper(str(part.address[0].country_id.name))
                country_list.append(cntry)


    from xml.dom.minidom import parse, parseString
    ad = tools.config['addons_path'] # check for base module path also
    module_path = os.path.join(ad, 'google_earth/world_country.kml')
    dom1 = parse(module_path) # parse an XML file by name
    placemarks = dom1.getElementsByTagName('Placemark')
    dict_country = {}
    for place in placemarks:
        name = place.getElementsByTagName('name')
        value_name = " ".join(t.nodeValue for t in name[0].childNodes if t.nodeType == t.TEXT_NODE)
        cord = place.getElementsByTagName('coordinates')
        value_cord = " ".join(t.nodeValue for t in cord[0].childNodes if t.nodeType == t.TEXT_NODE)
        if value_name in country_list:
            dict_country[value_name] = value_cord


    for country in country_list:
        print country
        cooridinate = dict_country[country]

#        print cooridinate

        if country == 'TAIWAN':

#    if address_with_country_ids:
#        for id in address_with_country_ids:
#            add = address_obj.browse(cr, uid, id, context)
#            address = ' '
#            if add.city:
#                address += str(add.city)
#            if add.state_id:
#                address += ', '
#                address += str(add.state_id.name)
#            if add.country_id:
#                address += ', '
#                address += str(add.country_id.name)
#            addresslist.append(address)
#    elif address_with_state_ids:
#        for id in address_with_state_ids:
#            add = address_obj.browse(cr, uid, id, context)
#            address = ' '
#            if add.city:
#                address += str(add.city)
#            if add.state_id:
#                address += ', '
#                address += str(add.state_id.name)
#            if add.country_id:
#                address += ', '
#                address += str(add.country_id.name)
#            addresslist.append(address)
#    elif address_with_city_ids:
#        for id in address_with_city_ids:
#            add = address_obj.browse(cr, uid, id, context)
#            address = ' '
#            if add.city:
#                address += str(add.city)
#            if add.state_id:
#                address += ', '
#                address += str(add.state_id.name)
#            if add.country_id:
#                address += ', '
#                address += str(add.country_id.name)
#            addresslist.append(address)
#    else:
#        raise wizard.except_wizard('Warning','Region has not defined')
#        return {}

#        for add in addresslist:
#            coordinates.sort(coordinates.append(geocode(add)))
#        for coordinate in coordinates:
#            coordinates_text += coordinate + '\n\t'


    #    kml creation start
            kmlDoc = xml.dom.minidom.Document()
            kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2','kml')
            kmlElement.setAttribute('xmlns','http://www.opengis.net/kml/2.2')
            kmlElement = kmlDoc.appendChild(kmlElement)

            documentElement = kmlDoc.createElement('Document')
            documentElement = kmlElement.appendChild(documentElement)

            documentElement1 = kmlDoc.createElement('name')
            nameText1 = documentElement1.appendChild(kmlDoc.createTextNode('TEST'))
            documentElement22 = kmlDoc.createElement('description')
            desc22 = documentElement22.appendChild(kmlDoc.createTextNode('DESCripition'))

            documentElement.appendChild(documentElement1)
            documentElement.appendChild(documentElement22)

            styleElement = kmlDoc.createElement('Style')
        #    styleElement = kmlDoc.EndElement(style)
            styleElement.setAttribute('id','transBluePoly')

            linestyleElement = kmlDoc.createElement('LineStyle')
        #    colorElement = kmlDoc.createElement('color')
        #    colorElement.appendChild(kmlDoc.createTextNode('80000000'))
        #    linestyleElement.appendChild(colorElement)

#            widthElement = kmlDoc.createElement('width')#today
#            widthElement.appendChild(kmlDoc.createTextNode('1.5'))
            colorElement = kmlDoc.createElement('color')
            colorElement.appendChild(kmlDoc.createTextNode('cc000000'))
#            linestyleElement.appendChild(widthElement)
            linestyleElement.appendChild(colorElement)
            styleElement.appendChild(linestyleElement)


#
#            <BalloonStyle><bgColor>ffffffff</bgColor><text><![CDATA[
#            <b><font color="#CC0000" size="+2">$[name]</font></b>
#            <br/><br/>$[description]<br/>
#            ]]></text></BalloonStyle>

            ballonElement = kmlDoc.createElement('BalloonStyle')
            ballonbgElement = kmlDoc.createElement('bgColor')
            ballonbgElement.appendChild(kmlDoc.createTextNode('ffffffff'))
            balloontextElement = kmlDoc.createElement('text')
            balloontextElement.appendChild(kmlDoc.createTextNode('TESSTT'))
            ballonElement.appendChild(ballonbgElement)
            ballonElement.appendChild(balloontextElement)
            styleElement.appendChild(ballonElement)

            polystyleElement = kmlDoc.createElement('PolyStyle')
            polycolorElement = kmlDoc.createElement('color')
            polycolorElement.appendChild(kmlDoc.createTextNode('59009900'))
            polyfillElement = kmlDoc.createElement('fill')
            polyfillElement.appendChild(kmlDoc.createTextNode('1'))
            polyoutlineElement = kmlDoc.createElement('outline')
            polyoutlineElement.appendChild(kmlDoc.createTextNode('1'))

            polystyleElement.appendChild(polycolorElement)
            polystyleElement.appendChild(polyfillElement)
            polystyleElement.appendChild(polyoutlineElement)
        #    fillElement = kmlDoc.createElement('fill')
        #    fillElement.appendChild(kmlDoc.createTextNode('1'))
        #    polystyleElement.appendChild(fillElement)
        #    outlineElement = kmlDoc.createElement('outline')
        #    outlineElement.appendChild(kmlDoc.createTextNode('1'))
        #    polystyleElement.appendChild(outlineElement)
            styleElement.appendChild(polystyleElement)
            documentElement.appendChild(styleElement)

            folderElement = kmlDoc.createElement('Folder')
            foldernameElement = kmlDoc.createElement('name')
            foldernameElement.appendChild(kmlDoc.createTextNode('Folder nameeeeeeeee'))
            folderElement.appendChild(foldernameElement)

            placemarkElement = kmlDoc.createElement('Placemark')
            placemarknameElement = kmlDoc.createElement('name')
            placemarknameText = kmlDoc.createTextNode(country)
            placemarkdescElement = kmlDoc.createElement('description')
            placemarkdescElement.appendChild(kmlDoc.createTextNode('Desctiptionnnnnn'))
            placemarknameElement.appendChild(placemarknameText)

            placemarkstyleElement = kmlDoc.createElement('Style')
            placemarkpolystyleElement = kmlDoc.createElement('PolyStyle')
            placemarkcolorrElement = kmlDoc.createElement('color')
            placemarkcolorrElement.appendChild(kmlDoc.createTextNode('59009900'))
            placemarkpolystyleElement.appendChild(placemarkcolorrElement)
            placemarkstyleElement.appendChild(placemarkpolystyleElement)
            placemarkdescElement.appendChild(kmlDoc.createTextNode('Desctiptionnnnnn'))

            placemarkElement.appendChild(placemarknameElement)
            placemarkElement.appendChild(placemarkdescElement)
            placemarkElement.appendChild(placemarkstyleElement)

#            <Style><PolyStyle>
#        <color>59009900</color>
#        </PolyStyle></Style>

        #    descriptionElement = kmlDoc.createElement('description')
        #    desc = """<![CDATA[Terre Haute City Council<br>District 4<br>Councilman: Todd Nation<br>
        #    website: <a href="http://www.toddnation.com">toddnation.com</a>]]>"""
        #    cdataElement = kmlDoc.createElement('![CDATA[')
        #    descriptionElement.appendChild(cdataElement)
        #    descriptionText = kmlDoc.createTextNode(desc)
        #    descriptionElement.appendChild(descriptionText)
        #    placemarkElement.appendChild(descriptionElement)
            styleurlElement = kmlDoc.createElement('styleUrl')
            styleurlElement.appendChild(kmlDoc.createTextNode('#transBluePoly'))
            placemarkElement.appendChild(styleurlElement)

            geometryElement = kmlDoc.createElement('MultiGeometry')
            polygonElement = kmlDoc.createElement('Polygon')

#            extrudeElement = kmlDoc.createElement('extrude')
#            extrudeElement.appendChild(kmlDoc.createTextNode('1'))
#            polygonElement.appendChild(extrudeElement)

#            altitudemodeElement = kmlDoc.createElement('altitudeMode')today
#            altitudemodeElement.appendChild(kmlDoc.createTextNode('relativeToGround'))
#            polygonElement.appendChild(altitudemodeElement)
#
            outerboundaryisElement = kmlDoc.createElement('outerBoundaryIs')
            linearringElement = kmlDoc.createElement('LinearRing')

        #    tessellateElement = kmlDoc.createElement('tessellate')
        #    tessellateElement.appendChild(kmlDoc.createTextNode('1'))
        #    linearringElement.appendChild(tessellateElement)

            coordinatesElemenent = kmlDoc.createElement('coordinates')
        #    coordinatesElemenent.appendChild(kmlDoc.createTextNode(coordinates_text))
            coordinatesElemenent.appendChild(kmlDoc.createTextNode(cooridinate))
            linearringElement.appendChild(coordinatesElemenent)

            outerboundaryisElement.appendChild(linearringElement)
            polygonElement.appendChild(outerboundaryisElement)
            geometryElement.appendChild(polygonElement)
            placemarkElement.appendChild(geometryElement)

            folderElement.appendChild(placemarkElement)
            documentElement.appendChild(folderElement)
#            documentElement.appendChild(placemarkElement) today

    # This writes the KML Document to a file.
    kmlFile = open(fileName, 'w')
    kmlFile.write(kmlDoc.toxml())
    kmlFile.close()
    return {}

class customer_on_map(wizard.interface):

    states = {
       'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end','Cancel'),('map','Get Partners on map')]}
                },
         'map': {
            'actions': [create_kml],
            'result': {'type': 'state', 'state': 'end'}
                }
            }
customer_on_map('layers.region.catery')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: