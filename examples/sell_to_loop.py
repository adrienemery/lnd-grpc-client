close = list(ln.list_channels_and_fees().query("balanced > 0.95 and active == True").chan_id)

for c in close:
	ln.lnd.close_channel(ln.get_peer_cp(c), sat_per_vbyte=1)


ln.lnd.open_channel("021c97a90a411ff2b10dc2a8e32de2f29d2fa49d41bfbb52bd416e460db0747d0d",65000000,spend_unconfirmed=True,sat_per_byte=1)