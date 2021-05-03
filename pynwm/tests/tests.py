import pynwm

station_id = 22798751  # mississippi

a = pynwm.data_service.ShortRange(station_id, use_examples=True)
print(a.data)
a.to_df()
plot = a.plot()
plot.show()

a = pynwm.data_service.MediumRange(station_id, use_examples=True)
print(a.data)
a.to_df()
plot = a.plot()
plot.show()

a = pynwm.data_service.LongRange(station_id, use_examples=True)
print(a.data)
a.to_df()
plot = a.plot()
plot.show()
