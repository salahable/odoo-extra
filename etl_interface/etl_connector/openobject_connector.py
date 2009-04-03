#!/usr/bin/python
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
import etl
import tools
from osv import osv, fields

class etl_connector_openobject(osv.osv):
    _name='etl.connector'
    _inherit='etl.connector'
    
    _columns={
              'uri' : fields.char('URL Path', size=64), 
              'db' : fields.char('Database', size=64), 
              'login' : fields.char('Login Name', size=64), 
              'passwd' : fields.char('Password', size=64), 
              'obj' : fields.char('Object', size=64), 
              'con_type' : fields.char('Connection Type', size=64), 
    }
    
    
    def onchange_type(self, cr, uid,ids, type):
        res=super(etl_connector_openobject, self).onchange_type(cr,uid,ids,type)
        val=res.get('value',{})
        if type and type=='openobject_connector':
            val['obj']= '/xmlrpc/object'
            val['con_type']= 'xmlrpc'                
        return {'value':val}
        
    def create_instance(self, cr, uid, id , context={}, data={}):
        val = super(etl_connector_openobject, self).create_instance(cr, uid, id, context, data)
        con=self.browse(cr, uid, id)
        if con.type == 'openobject_connector':
            val = etl.connector.openobject_connector(con.uri, cr.dbname, con.login, con.passwd, con.obj, con.con_type) 
        return val
        
etl_connector_openobject()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
