# -*- coding: utf-8 -*-

from random import randint
import qrcode
from io import StringIO
import io
import xml.etree.ElementTree as ET
from odoo.tools.image import image_data_uri
from xml.etree.ElementTree import tostring
from lxml import etree
import requests
import urllib3
import base64
from io import StringIO
import tarfile
import gzip
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import xmltodict
from bs4 import BeautifulSoup
import pprint
import json
from datetime import datetime, timedelta, date
from odoo.http import request, Response
import logging
import uuid
import dateutil.parser
from dateutil.relativedelta import relativedelta
import hashlib
from . import as_amount_to_text_es
_logger = logging.getLogger(__name__)

# -*- coding: utf-8 -*-

class AccountMoveModelos(models.Model):
    _inherit="account.move"
    def convertir_numero_a_literal(self, amount):
        amt_en = as_amount_to_text_es.amount_to_text(amount, 'BOLIVIANOS')
        return amt_en
    
    def as_verifica_comunicacion_xml(self, requerido):
        listaventas=[]
        nit=''
        razon_social=''
        municipio=''
        telefono=''
        numeroFactura=''
        cuf=''
        cufd=''
        codigoSucursal=''
        direccion=''
        codigoPuntoVenta=''
        fechaEmision=''
        nombreRazonSocial=''
        codigoTipoDocumentoIdentidad=''
        numeroDocumento=''
        complemento=''
        codigoCliente=''
        codigoMetodoPago=''
        numeroTarjeta=''
        montoTotal=0.00
        montoTotalSujetoIva=''
        codigoMoneda=''
        tipoCambio=''
        montoTotalMoneda=''
        montoGiftCard =''
        descuentoAdicional =0.00
        codigoExcepcion=''
        cafc=''
        leyenda=''
        usuario=''
        codigoDocumentoSector=''
        actividadEconomica=''
        codigoProductoSin= ''
        codigoProducto= ''
        descripcion= ''
        cantidad= 0.00
        unidadMedida= ''
        precioUnitario= 0.00
        montoDescuento = 0.00
        subTotal= 0.00
        numeroSerie=''
        numeroImei=''
        subtotalcalculado=0.00
        acumulador_total_neto=0.00
        if self.as_xml_invoice != False and self.move_type == 'out_invoice':
            body = base64.b64decode(self.as_xml_invoice).decode('UTF-8')
            try:
                res_xml = ET.fromstring(body)
                # codigoMensaje = BeautifulSoup(body.text,"xml").find()
                if ET.fromstring(body).find('.//cabecera/nitEmisor') is not None:
                    nit=ET.fromstring(body).find('.//cabecera/nitEmisor').text
                    
                if ET.fromstring(body).find('.//cabecera/razonSocialEmisor') is not None:
                    razon_social=ET.fromstring(body).find('.//cabecera/razonSocialEmisor').text
                    
                if ET.fromstring(body).find('.//cabecera/municipio') is not None:
                    municipio=ET.fromstring(body).find('.//cabecera/municipio').text
                
                if ET.fromstring(body).find('.//cabecera/telefono') is not None:
                    telefono=ET.fromstring(body).find('.//cabecera/telefono').text
                    
                if ET.fromstring(body).find('.//cabecera/numeroFactura') is not None:
                    numeroFactura=ET.fromstring(body).find('.//cabecera/numeroFactura').text
                
                if ET.fromstring(body).find('.//cabecera/cuf') is not None:
                    cuf=ET.fromstring(body).find('.//cabecera/cuf').text
                    
                if ET.fromstring(body).find('.//cabecera/cufd') is not None:
                    cufd=ET.fromstring(body).find('.//cabecera/cufd').text
                    
                if ET.fromstring(body).find('.//cabecera/codigoSucursal') is not None:
                    codigoSucursal=ET.fromstring(body).find('.//cabecera/codigoSucursal').text  
                    
                if ET.fromstring(body).find('.//cabecera/direccion') is not None:
                    direccion=ET.fromstring(body).find('.//cabecera/direccion').text
                    
                if ET.fromstring(body).find('.//cabecera/codigoPuntoVenta') is not None:
                    codigoPuntoVenta=ET.fromstring(body).find('.//cabecera/codigoPuntoVenta').text
                
                if ET.fromstring(body).find('.//cabecera/fechaEmision') is not None:
                    fechaEmision=ET.fromstring(body).find('.//cabecera/fechaEmision').text 
                    
                if ET.fromstring(body).find('.//cabecera/nombreRazonSocial') is not None:
                    nombreRazonSocial=ET.fromstring(body).find('.//cabecera/nombreRazonSocial').text 
                    
                if ET.fromstring(body).find('.//cabecera/codigoTipoDocumentoIdentidad') is not None:
                    codigoTipoDocumentoIdentidad=ET.fromstring(body).find('.//cabecera/codigoTipoDocumentoIdentidad').text  
                
                if ET.fromstring(body).find('.//cabecera/numeroDocumento') is not None:
                    numeroDocumento=ET.fromstring(body).find('.//cabecera/numeroDocumento').text 
                    
                if ET.fromstring(body).find('.//cabecera/complemento') is not None:
                    complemento=ET.fromstring(body).find('.//cabecera/complemento').text 
                    if complemento == 'False':
                        complemento=''
                    else:
                        complemento=ET.fromstring(body).find('.//cabecera/complemento').text
                    
                if ET.fromstring(body).find('.//cabecera/codigoCliente') is not None:
                    codigoCliente=ET.fromstring(body).find('.//cabecera/codigoCliente').text 
                
                if ET.fromstring(body).find('.//cabecera/codigoMetodoPago') is not None:
                    codigoMetodoPago=ET.fromstring(body).find('.//cabecera/codigoMetodoPago').text 
                
                if ET.fromstring(body).find('.//cabecera/numeroTarjeta') is not None:
                    numeroTarjeta =ET.fromstring(body).find('.//cabecera/numeroTarjeta').text 
                
                if ET.fromstring(body).find('.//cabecera/montoTotal') is not None:
                    montoTotal =float(ET.fromstring(body).find('.//cabecera/montoTotal').text)
                else:
                    montoTotal=0.00
                
                if ET.fromstring(body).find('.//cabecera/montoTotalSujetoIva') is not None:
                    montoTotalSujetoIva=ET.fromstring(body).find('.//cabecera/montoTotalSujetoIva').text 
                    
                if ET.fromstring(body).find('.//cabecera/codigoMoneda') is not None:
                    codigoMoneda=ET.fromstring(body).find('.//cabecera/codigoMoneda').text 
                    
                if ET.fromstring(body).find('.//cabecera/tipoCambio') is not None:
                    tipoCambio=ET.fromstring(body).find('.//cabecera/tipoCambio').text
                
                if ET.fromstring(body).find('.//cabecera/montoTotalMoneda') is not None:
                    montoTotalMoneda=ET.fromstring(body).find('.//cabecera/montoTotalMoneda').text
                    
                if ET.fromstring(body).find('.//cabecera/montoGiftCard') is not None:
                    montoGiftCard=ET.fromstring(body).find('.//cabecera/montoGiftCard').text
                    
                if ET.fromstring(body).find('.//cabecera/descuentoAdicional').text is not None:
                    descuentoAdicional =float(ET.fromstring(body).find('.//cabecera/descuentoAdicional').text)   
                else:
                    descuentoAdicional=0.00
                    
                if ET.fromstring(body).find('.//cabecera/codigoExcepcion') is not None:
                    codigoExcepcion=ET.fromstring(body).find('.//cabecera/codigoExcepcion').text
                    
                if ET.fromstring(body).find('.//cabecera/cafc') is not None:
                    cafc=ET.fromstring(body).find('.//cabecera/cafc').text
                
                if ET.fromstring(body).find('.//cabecera/leyenda') is not None:
                    leyenda=ET.fromstring(body).find('.//cabecera/leyenda').text
                    
                if ET.fromstring(body).find('.//cabecera/usuario') is not None:
                    usuario=ET.fromstring(body).find('.//cabecera/usuario').text
                    
                if ET.fromstring(body).find('.//cabecera/codigoDocumentoSector') is not None:
                    codigoDocumentoSector=ET.fromstring(body).find('.//cabecera/codigoDocumentoSector').text
                    
                if ET.fromstring(body).find('.//detalle') is not None:
                    linea_detalle=ET.fromstring(body).findall('.//detalle')
                    for line in linea_detalle:
                        if line.find('.//actividadEconomica').text is not None:
                            actividadEconomica=line.find('.//actividadEconomica').text
                        else:
                            actividadEconomica=''
                        
                        if line.find('.//codigoProductoSin').text is not None:
                            codigoProductoSin=line.find('.//codigoProductoSin').text
                        else:
                            codigoProductoSin=''
                            
                        if line.find('.//codigoProducto').text is not None:
                            codigoProducto=line.find('.//codigoProducto').text
                        else:
                            codigoProducto=''
                            
                        if line.find('.//descripcion').text is not None:
                            descripcion=line.find('.//descripcion').text
                        else:
                            descripcion=''
                        
                        if line.find('.//cantidad').text is not None:
                            cantidad=float(line.find('.//cantidad').text)
                        else:
                            cantidad=0.00
                            
                        if line.find('.//unidadMedida').text is not None:
                            unidad=line.find('.//unidadMedida').text
                            valor=self.env['as.siat.catalogos'].search([('as_group', '=', 'UNIDAD_MEDIDA'),('as_code','=',unidad)],limit=1)
                            unidadMedida=valor.name
                        else:
                            unidadMedida=''
                            
                        if line.find('.//precioUnitario').text is not None:
                            precioUnitario=float(line.find('.//precioUnitario').text)
                        else:
                            precioUnitario=0.00
                            
                        if line.find('.//montoDescuento').text is not None:
                            montoDescuento =line.find('.//montoDescuento').text
                        else:
                            montoDescuento=0.00
                            
                        if line.find('.//subTotal').text is not None:
                            subTotal =line.find('.//subTotal').text
                        else:
                            subTotal=0.00
                        
                        if line.find('.//numeroSerie').text is not None:
                            numeroSerie =line.find('.//numeroSerie').text
                        else:
                            numeroSerie=''
                        
                        if line.find('.//numeroImei').text is not None:
                            numeroImei =line.find('.//numeroImei').text
                        else:
                            numeroImei=''
                        if line.find('.//cantidad').text and line.find('.//precioUnitario').text and line.find('.//montoDescuento').text is not None:
                            subtotalcalculado=((float(line.find('.//cantidad').text) * float(line.find('.//precioUnitario').text)) - float(line.find('.//montoDescuento').text))
                            acumulador_total_neto+=subtotalcalculado
                        else:
                            subtotalcalculado=float(line.find('.//cantidad').text) * float(line.find('.//precioUnitario').text)
                            acumulador_total_neto+=subtotalcalculado
                        lineas={
                            'actividadEconomica':actividadEconomica,
                            'codigoProductoSin':codigoProductoSin,
                            'codigoProducto':codigoProducto,
                            'descripcion':descripcion,
                            'cantidad':cantidad,
                            'unidadMedida':unidadMedida,
                            'precioUnitario':precioUnitario,
                            'montoDescuento':montoDescuento ,
                            'subTotal':subTotal,
                            'numeroSerie':numeroSerie,
                            'numeroImei':numeroImei,
                            'subtotalcalculado':subtotalcalculado,
                            'acumulador_total_neto':acumulador_total_neto,
                            }
                        listaventas.append(lineas)
                        
            except ValueError:
                return 'Error'
        json={
            'nit':nit,
            'razonSocialEmisor':razon_social,
            'municipio':municipio,
            'telefono':telefono,
            'numeroFactura':numeroFactura, #variables no inicializadas
            'cuf':cuf,
            'cufd':cufd,
            'codigoSucursal':codigoSucursal,
            'direccion':direccion,
            'codigoPuntoVenta':codigoPuntoVenta,
            'fechaEmision':fechaEmision,
            'nombreRazonSocial':nombreRazonSocial,
            'codigoTipoDocumentoIdentidad':codigoTipoDocumentoIdentidad,
            'numeroDocumento':numeroDocumento,
            'complemento': complemento,
            'codigoCliente':codigoCliente,
            'codigoMetodoPago':codigoMetodoPago,
            'numeroTarjeta': numeroTarjeta,
            'montoTotal':montoTotal,
            'montoTotalSujetoIva':montoTotalSujetoIva,
            'codigoMoneda':codigoMoneda,
            'tipoCambio':tipoCambio,
            'montoTotalMoneda':montoTotalMoneda,
            'montoGiftCard':montoGiftCard ,
            'descuentoAdicional':descuentoAdicional ,
            'codigoExcepcion':codigoExcepcion,
            'cafc':cafc,
            'leyenda':leyenda,
            'usuario':usuario,
            'codigoDocumentoSector':codigoDocumentoSector,
            }
        json['contenido']= listaventas
        nit = json[str(requerido)]
        return nit
    def acumulador_de_totales(self, requerido):
        subtotalcalculado=0.00
        acumulador_total_neto=0.00
        if self.as_xml_invoice != False:
            body = base64.b64decode(self.as_xml_invoice).decode('UTF-8')
            try:
                if ET.fromstring(body).find('.//detalle') is not None:
                    linea_detalle=ET.fromstring(body).findall('.//detalle')
                    for line in linea_detalle:
                        if line.find('.//cantidad').text and line.find('.//precioUnitario').text and line.find('.//montoDescuento').text is not None:
                            subtotalcalculado=((float(line.find('.//cantidad').text) * float(line.find('.//precioUnitario').text)) - float(line.find('.//montoDescuento').text))
                            acumulador_total_neto+=subtotalcalculado
                        else:
                            subtotalcalculado=float(line.find('.//cantidad').text) * float(line.find('.//precioUnitario').text)
                            acumulador_total_neto+=subtotalcalculado
                        
            except ValueError:
                return 'Error'
        lineas={
            'acumulador_total_neto':acumulador_total_neto,
              }
        nit = lineas[str(requerido)]
        return nit
    
    def separar_qr(self):
        nit=''
        cuf=''
        numeroFactura=''
        if self.as_xml_invoice != False and self.move_type == 'out_invoice':
            body = base64.b64decode(self.as_xml_invoice).decode('UTF-8')
            try:
                res_xml = ET.fromstring(body)
                # codigoMensaje = BeautifulSoup(body.text,"xml").find()
                if ET.fromstring(body).find('.//cabecera/nitEmisor') is not None:
                    nit=ET.fromstring(body).find('.//cabecera/nitEmisor').text
                if ET.fromstring(body).find('.//cabecera/cuf') is not None:
                    cuf=ET.fromstring(body).find('.//cabecera/cuf').text
                if ET.fromstring(body).find('.//cabecera/numeroFactura') is not None:
                    numeroFactura=ET.fromstring(body).find('.//cabecera/numeroFactura').text
            except ValueError:
                return 'Error'
        # nit = self.partner_id.vat
        # nit=self.as_nit_emisor
        # cuf = self.as_unique_invoice_code
        # numero_fact = self.as_invoice_number
        if not nit:
            raise UserError(_("El nit del emisor esta vacio, verifique los datos que se estan enviando en el XML"))
        if not cuf:
            raise UserError(_("El cuf esta vacio, verifique los datos que se estan enviando en el XML"))
        if self.as_cuf:
            # concatenacion= 'https://siat.impuestos.gob.bo/facturacionv2/public/Qr.xhtml?nit='+str(nit)+'&cuf='+str(self.as_cuf)+'&numero='+str(numeroFactura)+'&t=1'
            concatenacion= 'https://siat.impuestos.gob.bo/consulta/QR?nit='+str(nit)+'&cuf='+str(cuf)+'&numero='+str(numeroFactura)+'&t=1'
            try:
                qr_img = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=0)
                qr_img.add_data(concatenacion)
                qr_img.make(fit=True)
                img = qr_img.make_image()
                # buffer = StringIO()
                buffer = io.BytesIO()
                img.save(buffer)
                qr_img = base64.b64encode(buffer.getvalue())
                return qr_img
            except:
                raise UserError(_('No se puedo generar el codigo QR'))
        else:
            raise UserError(_('El campo cuf esta vacio, verifique la pestaña de informacion computarizada'))
        
        

