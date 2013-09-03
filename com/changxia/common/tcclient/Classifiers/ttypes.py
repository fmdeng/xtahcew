#
# Autogenerated by Thrift
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#

from thrift.Thrift import *

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None



class DocParam:
  """
  Attributes:
   - uid
   - rawTitle
   - rawContent
   - title
   - content
   - pubtime
   - host
   - contentGroup
   - additionalInformation
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'uid', None, None, ), # 1
    (2, TType.STRING, 'rawTitle', None, None, ), # 2
    (3, TType.STRING, 'rawContent', None, None, ), # 3
    (4, TType.STRING, 'title', None, None, ), # 4
    (5, TType.STRING, 'content', None, None, ), # 5
    (6, TType.STRING, 'pubtime', None, None, ), # 6
    (7, TType.STRING, 'host', None, None, ), # 7
    (8, TType.STRING, 'contentGroup', None, None, ), # 8
    (9, TType.STRING, 'additionalInformation', None, None, ), # 9
  )

  def __init__(self, uid="", rawTitle="", rawContent="", title="", content="", pubtime="", host="", contentGroup="", additionalInformation="",):
    self.uid = uid
    self.rawTitle = rawTitle
    self.rawContent = rawContent
    self.title = title
    self.content = content
    self.pubtime = pubtime
    self.host = host
    self.contentGroup = contentGroup
    self.additionalInformation = additionalInformation

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.uid = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.rawTitle = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.rawContent = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.title = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.STRING:
          self.content = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.STRING:
          self.pubtime = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 7:
        if ftype == TType.STRING:
          self.host = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 8:
        if ftype == TType.STRING:
          self.contentGroup = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 9:
        if ftype == TType.STRING:
          self.additionalInformation = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('DocParam')
    if self.uid != None:
      oprot.writeFieldBegin('uid', TType.STRING, 1)
      oprot.writeString(self.uid)
      oprot.writeFieldEnd()
    if self.rawTitle != None:
      oprot.writeFieldBegin('rawTitle', TType.STRING, 2)
      oprot.writeString(self.rawTitle)
      oprot.writeFieldEnd()
    if self.rawContent != None:
      oprot.writeFieldBegin('rawContent', TType.STRING, 3)
      oprot.writeString(self.rawContent)
      oprot.writeFieldEnd()
    if self.title != None:
      oprot.writeFieldBegin('title', TType.STRING, 4)
      oprot.writeString(self.title)
      oprot.writeFieldEnd()
    if self.content != None:
      oprot.writeFieldBegin('content', TType.STRING, 5)
      oprot.writeString(self.content)
      oprot.writeFieldEnd()
    if self.pubtime != None:
      oprot.writeFieldBegin('pubtime', TType.STRING, 6)
      oprot.writeString(self.pubtime)
      oprot.writeFieldEnd()
    if self.host != None:
      oprot.writeFieldBegin('host', TType.STRING, 7)
      oprot.writeString(self.host)
      oprot.writeFieldEnd()
    if self.contentGroup != None:
      oprot.writeFieldBegin('contentGroup', TType.STRING, 8)
      oprot.writeString(self.contentGroup)
      oprot.writeFieldEnd()
    if self.additionalInformation != None:
      oprot.writeFieldBegin('additionalInformation', TType.STRING, 9)
      oprot.writeString(self.additionalInformation)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()
    def validate(self):
      if self.uid is None:
        raise TProtocol.TProtocolException(message='Required field uid is unset!')
      if self.rawTitle is None:
        raise TProtocol.TProtocolException(message='Required field rawTitle is unset!')
      if self.rawContent is None:
        raise TProtocol.TProtocolException(message='Required field rawContent is unset!')
      if self.title is None:
        raise TProtocol.TProtocolException(message='Required field title is unset!')
      if self.content is None:
        raise TProtocol.TProtocolException(message='Required field content is unset!')
      if self.pubtime is None:
        raise TProtocol.TProtocolException(message='Required field pubtime is unset!')
      if self.host is None:
        raise TProtocol.TProtocolException(message='Required field host is unset!')
      if self.contentGroup is None:
        raise TProtocol.TProtocolException(message='Required field contentGroup is unset!')
      if self.additionalInformation is None:
        raise TProtocol.TProtocolException(message='Required field additionalInformation is unset!')
      return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class ConnectionError(Exception):

  thrift_spec = (
  )

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('ConnectionError')
    oprot.writeFieldStop()
    oprot.writeStructEnd()
    def validate(self):
      return


  def __str__(self):
    return repr(self)

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
