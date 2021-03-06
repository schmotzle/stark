"""
Benedikt Schmotzle <code<at>schmotzle.info> - 2016
    STARK - v0.0.1
        STARK is a Binary Ninja plugin loosly based on the JARVIS IDA Pro plugin
	by Carlos Garcia Prado.
	It is also using code from BinjaDock by defunct as a basis.

MIT License
Copyright (c) <2017> <Benedikt Schmotzle>                                                                                         
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from binaryninja import *
from defunct.widgets import BinjaWidget
from functools import partial
import defunct.widgets
import epdb
import operator

ws32_ordinals = {
'1'  : 'accept',
'2'  : 'bind',
'3'  : 'closesocket',
'4'  : 'connect',
'5'  : 'getpeername',
'6'  : 'getsockname',
'7'  : 'getsockopt',
'8'  : 'htonl',
'9'  : 'htons',
'10' : 'ioctlsocket',
'11' : 'inet_addr',
'12' : 'inet_ntoa',
'13' : 'listen',
'14' : 'ntohl',
'15' : 'ntohs',
'16' : 'recv',
'17' : 'recvfrom',
'18' : 'select',
'19' : 'send',
'20' : 'sendto',
'21' : 'setsockopt',
'22' : 'shutdown',
'23' : 'socket',
'24' : 'GetAddrInfoW',
'25' : 'GetNameInfoW',
'26' : 'WSApSetPostRoutine',
'27' : 'FreeAddrInfoW',
'28' : 'WPUCompleteOverlappedRequest',
'29' : 'WSAAccept',
'30' : 'WSAAddressToStringA',
'31' : 'WSAAddressToStringW',
'32' : 'WSACloseEvent',
'33' : 'WSAConnect',
'34' : 'WSACreateEvent',
'35' : 'WSADuplicateSocketA',
'36' : 'WSADuplicateSocketW',
'37' : 'WSAEnumNameSpaceProvidersA',
'38' : 'WSAEnumNameSpaceProvidersW',
'39' : 'WSAEnumNetworkEvents',
'40' : 'WSAEnumProtocolsA',
'41' : 'WSAEnumProtocolsW',
'42' : 'WSAEventSelect',
'43' : 'WSAGetOverlappedResult',
'44' : 'WSAGetQOSByName',
'45' : 'WSAGetServiceClassInfoA',
'46' : 'WSAGetServiceClassInfoW',
'47' : 'WSAGetServiceClassNameByClassIdA',
'48' : 'WSAGetServiceClassNameByClassIdW',
'49' : 'WSAHtonl',
'50' : 'WSAHtons',
'51' : 'gethostbyaddr',
'52' : 'gethostbyname',
'53' : 'getprotobyname',
'54' : 'getprotobynumber',
'55' : 'getservbyname',
'56' : 'getservbyport',
'57' : 'gethostname',
'58' : 'WSAInstallServiceClassA',
'59' : 'WSAInstallServiceClassW',
'60' : 'WSAIoctl',
'61' : 'WSAJoinLeaf',
'62' : 'WSALookupServiceBeginA',
'63' : 'WSALookupServiceBeginW',
'64' : 'WSALookupServiceEnd',
'65' : 'WSALookupServiceNextA',
'66' : 'WSALookupServiceNextW',
'67' : 'WSANSPIoctl',
'68' : 'WSANtohl',
'69' : 'WSANtohs',
'70' : 'WSAProviderConfigChange',
'71' : 'WSARecv',
'72' : 'WSARecvDisconnect',
'73' : 'WSARecvFrom',
'74' : 'WSARemoveServiceClass',
'75' : 'WSAResetEvent',
'76' : 'WSASend',
'77' : 'WSASendDisconnect',
'78' : 'WSASendTo',
'79' : 'WSASetEvent',
'80' : 'WSASetServiceA',
'81' : 'WSASetServiceW',
'82' : 'WSASocketA',
'83' : 'WSASocketW',
'84' : 'WSAStringToAddressA',
'85' : 'WSAStringToAddressW',
'86' : 'WSAWaitForMultipleEvents',
'87' : 'WSCDeinstallProvider',
'88' : 'WSCEnableNSProvider',
'89' : 'WSCEnumProtocols',
'90' : 'WSCGetProviderPath',
'91' : 'WSCInstallNameSpace',
'92' : 'WSCInstallProvider',
'93' : 'WSCUnInstallNameSpace',
'94' : 'WSCUpdateProvider',
'95' : 'WSCWriteNameSpaceOrder',
'96' : 'WSCWriteProviderOrder',
'97' : 'freeaddrinfo',
'98' : 'getaddrinfo',
'99' : 'getnameinfo',
'101' : 'WSAAsyncSelect',
'102' : 'WSAAsyncGetHostByAddr',
'103' : 'WSAAsyncGetHostByName',
'104' : 'WSAAsyncGetProtoByNumber',
'105' : 'WSAAsyncGetProtoByName',
'106' : 'WSAAsyncGetServByPort',
'107' : 'WSAAsyncGetServByName',
'108' : 'WSACancelAsyncRequest',
'109' : 'WSASetBlockingHook',
'110' : 'WSAUnhookBlockingHook',
'111' : 'WSAGetLastError',
'112' : 'WSASetLastError',
'113' : 'WSACancelBlockingCall',
'114' : 'WSAIsBlocking',
'115' : 'WSAStartup',
'116' : 'WSACleanup',
'151' : '__WSAFDIsSet',
'500' : 'WEP'
}

class StatisticsWidget(BinjaWidget):
    """Binja Statistics plugin
        Basic binary statistics.
    """
    def __init__(self, name, labels=[]):

        super(StatisticsWidget, self).__init__(name)
        self._table = QtWidgets.QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(labels)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self.setLayout(QtWidgets.QStackedLayout())
        self.layout().addWidget(self._table)
        self.setObjectName('BNPlugin_Statistics')

    @QtCore.pyqtSlot(list)
    def build_table(self, bv, get_data):
        """ Scans a binary view function xrefs 
        :param bv:  The BinaryView to use
        :type bv: binaryninja.BinaryView
        :return:
        """
        self._view = bv

	data = get_data(bv)
        self._table.setRowCount(len(data))

	i = 0
        for it in data:
            name = QtWidgets.QTableWidgetItem(it[0])
            name.setFlags(Qt.ItemIsEnabled)
	    if isInt(it[1]):
	            xrefs = QtWidgets.QTableWidgetItem(str(it[1]))
	    else:
	            xrefs = QtWidgets.QTableWidgetItem(it[1])
            xrefs.setFlags(Qt.ItemIsEnabled)
            xrefs.setForeground(QtGui.QColor(162, 217, 175))
            self._table.setItem(i, 1, xrefs)
            self._table.setItem(i, 0, name)
	    i = i+1

        self._table.cellDoubleClicked.connect(self.cell_action)
        self._core.show()
        self._core.selectTab(self)
        self.show()

    def cell_action(self, row, column):
        # TODO: view highlighting
        self.navigate(self._view, self._table.item(row, 0).text(), self._table.item(row, 1).text())

    def navigate(self, bv, name, val):
	try:
		address = bv.get_symbol_by_raw_name(name).address
	except:
		funcs = filter(lambda x: x.name == name, bv.functions)
		if len(funcs) > 0:
			address = filter(lambda x: x.name == name, bv.functions)[0].start
		else:
			if "0x" in val:
				address = int(val, 16)
			else:
				address = int(val)

        bv.navigate('Graph:' + bv.view_type, address)

def get_exts(bv):
	stat = {}
	for f in bv.functions:
		for bb in f.medium_level_il:
			for i in bb:
				if i.operation == MediumLevelILOperation.MLIL_CALL:
					try:
						bv.get_symbol_by_raw_name(f.name) # if it is has no symbol we don't count it
						if f.name in stat:
							stat[f.name] = stat[f.name] + 1
						else:
							stat[f.name] = 0
					except:
						continue

	sort = sorted(stat.items(), key=operator.itemgetter(1))
	sort.reverse()

	return sort


def get_bbs(bv):
	stat = {}
	for f in bv.functions:
		stat[f.name] = len(f.basic_blocks)

	sort = sorted(stat.items(), key=operator.itemgetter(1))
	sort.reverse()
	
	return sort

def get_xrefs(bv):
	stat = {}
	for f in bv.functions:
		stat[f.name] = len(bv.get_code_refs(f.start))

	sort = sorted(stat.items(), key=operator.itemgetter(1))
	sort.reverse()
	
	return sort

def get_calls(fun, bv):
	calls = [] 
	for bb in fun.medium_level_il:
		log_info(bb)
		for i in bb:
			log_info(i)
			if i.operation == MediumLevelILOperation.MLIL_CALL or i.operation == MediumLevelILOperation.MLIL_CALL_UNTYPED:
				log_info(i)
				if isinstance(i.dest.operands[0], MediumLevelILInstruction):
					address = i.dest.operands[0].operands[0]
				else:
					address = i.dest.operands[0]
				
				log_info(address)
				if not isinstance(address, long):
					# TODO: if register has known value test for that..
					continue

				name = bv.get_symbol_at(address)
				if not name:
					name = bv.get_function_at(address)
				log_info(name)

				calls.append([name.name, hex(address)])
				

	return calls

def get_strings(fun, bv):
	strings = [] 
	for bb in fun.medium_level_il:
		log_info(bb)
		for i in bb:
			log_info(i)
			try:
				i.operands
			except:
				continue
			for p in i.operands:
				log_info(p)
				if not isinstance(p, MediumLevelILInstruction):
					log_info(type(p))
					continue

				if p.operation == MediumLevelILOperation.MLIL_CONST and bv.get_segment_at(p.value.value):
					log_info("Found potential str")
					name = bv.read(p.value.value, 20).split("\x00")[0]
					strings.append([name, hex(p.value.value)])
#					filtered = filter(lambda x: x.start == p.value.value, bv.strings) 
#					if len(filtered) > 0:
#						strref = filtered[0]
##						name = bv.read(strref.start, strref.length)
#						strings.append([name, hex(p.value.value)])
#						log_info(name)

	return strings

def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

x = StatisticsWidget(name='Xrefs', labels=['Function', 'xrefs'])
b = StatisticsWidget(name='BBs', labels=['Function', 'bb'])
c = StatisticsWidget(name='Calls', labels=['Function', 'address'])
e = StatisticsWidget(name='External', labels=['Function', 'calls'])
s = StatisticsWidget(name='Strings', labels=['String', 'address'])


def xrefs(bv):
    x.build_table(bv, get_xrefs)

def bbs(bv):
    b.build_table(bv, get_bbs)

def exts(bv):
    e.build_table(bv, get_exts)

def calls(bv, fun):
    c.build_table(bv, partial(get_calls, fun))

def strings(bv, fun):
    s.build_table(bv, partial(get_strings, fun))

def ws2(bv, fun):

    for bb in fun.medium_level_il:
	for i in bb:
		if i.operation == MediumLevelILOperation.MLIL_CALL or i.operation == MediumLevelILOperation.MLIL_CALL_UNTYPED:
			log_info(i)
			if isinstance(i.dest.operands[0], MediumLevelILInstruction):
				address = i.dest.operands[0].operands[0]
			else:
				address = i.dest.operands[0]
			
			log_info(address)
			if not isinstance(address, long):
				# TODO: if register has known value test for that..
				continue

			sym = bv.get_symbol_at(address)

			if sym is not None:
				if "WS2_32" in sym.name:
					fun.set_comment(i.address, ws32_ordinals[sym.name.split("@")[0].split("_")[-1]])
			#    saved_name = sym.name
		        #    if sym.auto == True:
                #		bv.undefine_auto_symbol(sym)
		 #           else:
		  #              bv.undefine_user_symbol(sym)
	                
                   #         sym = types.Symbol(SymbolType.FunctionSymbol, address, saved_name+"LOL")
		    #        bv.define_user_symbol(sym)		
		#	    log_info(sym)


PluginCommand.register('Function xrefs', 'Show number of xrefs for each function', xrefs)
PluginCommand.register('Function bb', 'Show number of basic blocks for each function', bbs)
PluginCommand.register('Function external', 'Show number of calls to imported functions for each function', exts)
PluginCommand.register_for_function('Function calls', 'Show all calls out of the given function', calls)
PluginCommand.register_for_function('Function strings', 'Show all referenced strings of the given function', strings)
PluginCommand.register_for_function('Function ws2', 'Rename all ws2 calls in the function', ws2)
