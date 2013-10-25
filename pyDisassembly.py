#!/usr/bin/env python
import os
import re
import cmd

class DB_operation():

	def open(self):
		print 'DB_operation:open'

	def close(self):
		print 'DB_operation:close'

	def insert(self):
		print 'DB_operation:insert'
		
	def delete(self):
		print 'DB_operation:delete'

	def search(self):
		print 'DB_operation:search'

class VU_DB_Ops(DB_operation):

	def insert(self):
		super(MIPS_DB_Ops, self).__init__()
		print 'VU:insert'
		
	def delete(self):
		print 'VU:delete'

class MIPS_DB_Ops(DB_operation):

	def __init__(self): pass
#		super(MIPS_DB_Ops, self).__init__()

	def insert(self):
		print 'MIPS:insert'
		
	def delete(self):
		print 'MIPS:delete'

	def parseInstSet(self, instSet): pass
	def parseInstClass(self, instClass): pass
	def parsePageNum(self, pageNum): pass
	def parseInst(self, inst):
		inst_split = inst.split(' ')
		return (inst_split[0], inst_split[1], inst_split[2:])

class DB():

	Hash = {}

	def __init__(self, ops):
		self.op = ops
		self.cur_file = './mips32lib.txt'

	# evaluate instruction mask
	def evaluateMask(self, inst, field):
		mask = ""
		for i, iInst in enumerate(inst):
			m = re.match('[A-Za-z_]+', iInst)
			if m is not None:
				mask += "_" * int(field[i])
			else:
				mask += iInst
		return mask

	# and with mask
	def doMask(self, data, mask):
		similarity = 0
		for i, ch in enumerate(mask):
			if ch == '_':
				continue
			elif data[i] != ch:
				return (False, -1)
			else:
				similarity += 1

		return (True, similarity)

	# build DB using Hash table
	def buildDB(self):

		self.total_inst = 0

		file = open(self.cur_file)
		content = file.readlines()
		for eachLine in content:
			eachLine = eachLine.strip()
			raw_split = eachLine.split('#')	# split to several part, OP, field, description...
			self.total_inst += 1
			(instSet, instClass, pageNum, inst, field, format, discription) = raw_split
			(CMD, CMDBIN, inst_split) = self.op.parseInst(inst)
			field_split = field.split(' ')

			if len(inst_split) != len(field_split):
				print "################# WRONG INSTRUCTION! ################"

			# compute inst_mask for each instruction
			inst_mask = CMDBIN+self.evaluateMask(inst_split, field_split)

			# add to Hash
			if CMD in self.Hash:
				cur_num = len(self.Hash[CMD]) + 1

				self.Hash[CMD][cur_num] = {}
				self.Hash[CMD][cur_num]['cmd'] = CMD
				self.Hash[CMD][cur_num]['inst'] = inst
				self.Hash[CMD][cur_num]['field'] = field
				self.Hash[CMD][cur_num]['mask'] = inst_mask
				self.Hash[CMD][cur_num]['format'] = format
				self.Hash[CMD][cur_num]['discription'] = discription
				self.Hash[CMD][cur_num]['instset'] = instSet
				self.Hash[CMD][cur_num]['instclass'] = instClass
				self.Hash[CMD][cur_num]['pagenum'] = pageNum
			else:
				self.Hash[CMD] = {} 

				self.Hash[CMD][1] = {} 
				self.Hash[CMD][1]['cmd'] = CMD
				self.Hash[CMD][1]['inst'] = inst
				self.Hash[CMD][1]['field'] = field
				self.Hash[CMD][1]['mask'] = inst_mask
				self.Hash[CMD][1]['format'] = format
				self.Hash[CMD][1]['discription'] = discription
				self.Hash[CMD][1]['instset'] = instSet
				self.Hash[CMD][1]['instclass'] = instClass
				self.Hash[CMD][1]['pagenum'] = pageNum

	# change DB
	def updateDB(self, inputfile = './mips32lib.txt'):
		self.cur_file = inputfile
		self.buildDB()

	# parse specific mips instruction
	def parseCmd(self, origmachcode):
		flag = 0
		binary = bin(int(origmachcode, 16))[2:]
		binary = '0'*(32-len(binary)) + binary

		maxSimilar = -1 
		foundCmd = '' 
		foundIdx = -1
		for eachCmd in self.Hash:
			for eachIdx in self.Hash[eachCmd]:
				eachMask = self.Hash[eachCmd][eachIdx]['mask']
				(isFound, similarity) = self.doMask(binary, eachMask)
				if isFound:
					if (similarity > maxSimilar):
						maxSimilar = similarity
						foundCmd = eachCmd
						foundIdx = eachIdx

		if not foundCmd:
			print "ERROR: Invalid Instruction"
		else:
			format = self.Hash[foundCmd][foundIdx]['format']
			inst   = self.Hash[foundCmd][foundIdx]['inst']
			field  = self.Hash[foundCmd][foundIdx]['field']
			discription  = self.Hash[foundCmd][foundIdx]['discription']

			inst_split = inst.split(' ')[2:]
			field_split = field.split(' ')
			rest_binary = binary[6:]			# FIXME: should be more general

			format_str = ""
			offset = 0
			# FIXME: should be more general
			for i, ch in enumerate(inst_split):
				regexp_reg = re.match("([A-Za-z]+)", inst_split[i])
				if regexp_reg is not None:
					match_str = regexp_reg.group()
					regexp_rt = re.search("rt", match_str)
					regexp_rs = re.search("rs", match_str)
					regexp_immediate = re.search("immediate", match_str)

					if regexp_rt is not None:
						reg_num = rest_binary[offset : offset+int(field_split[i])]
						format = format.replace("rt", "r"+str(int(reg_num, 2)))
					elif regexp_rs is not None:
						reg_num = rest_binary[offset : offset+int(field_split[i])]
						format = format.replace("rs", "r"+str(int(reg_num, 2)))
					elif regexp_immediate is not None:
						reg_num = rest_binary[offset : offset+int(field_split[i])]
						format = format.replace("immediate", str(hex(int(reg_num, 2))))

					offset += int(field_split[i])

			print format

#class Console(cmd.Cmd):
#	"""Simple command processor example."""
#
#	def __init__(self, prompt):
#		super(Console, self).__init__()
#		self.prompt = prompt
#
#	def do_greet(self, line):
#		print "hello"
#
#	def do_EOF(self, line):
#		return True

if __name__ == '__main__':
#	console = Console('prompt >')
#	console.cmdloop()
#		db_ops = VU()
#		db = DB(db_ops)
#		db.op.insert()
#		db.op.delete()
#		db.op.search()
		db_ops = MIPS_DB_Ops()
		db = DB(db_ops)
		db.updateDB()

		db.parseCmd("34002345")
