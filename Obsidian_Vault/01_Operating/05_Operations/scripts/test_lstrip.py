s = r'\\Torus_Smart_Ticket_Cycle'
print('before:', repr(s))
print('after lstrip:', repr(s.lstrip(r'\\')))
print('startswith:', s.startswith(r'\\'))
print('after lstrip2:', repr(s.lstrip('\\')))
