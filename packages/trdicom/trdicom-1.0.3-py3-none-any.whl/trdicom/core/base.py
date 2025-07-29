from pynetdicom import AE


class BaseNetDicom:

    def __init__(self, ae_title='ZY-AE', host='127.0.0.1', port=11112, **kwargs):
        self.ae_title = ae_title
        self.host = host
        self.port = port
        self.ae = AE(ae_title=ae_title)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def test(self):
        print("test dicom server", self.ae)

    def _log(self, event):
        requestor = event.assoc.requestor
        timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        msg = "\n\n{} from ({}, {}) at {}\n\n".format(
            event._event.description, requestor.address, requestor.port, timestamp
        )
        print(msg)

    def handle_echo(self, event):
        """Handle a C-ECHO service request.

        Parameters
        ----------
        event : evt.Event
            The C-ECHO service request event, this parameter is always
            present.
        logger : logging.Logger
            The logger to use, this parameter is only present because we
            bound ``evt.EVT_C_ECHO`` using a 3-tuple.

        Returns
        -------
        int or pydicom.dataset.Dataset
            The status returned to the peer AE in the C-ECHO response.
            Must be a valid C-ECHO status value as either an ``int`` or a
            ``Dataset`` object containing an (0000,0900) *Status* element.
        """
        # Every *Event* includes `assoc` and `timestamp` attributes
        #   which are the *Association* instance the event occurred in
        #   and the *datetime.datetime* the event occurred at
        self._log(event)

        # Return a *Success* status
        return 0x0000

    def after_store(self):
        raise NotImplementedError("after_store is not implemented")

    def handle_store(self, event):
        """Handle a C-STORE request event."""
        # Decode the C-STORE request's *Data Set* parameter to a pydicom Dataset
        self._log(event)

        ds = event.dataset

        # Add the File Meta Information
        ds.file_meta = event.file_meta

        self.after_store(event, ds)

        return 0x0000
