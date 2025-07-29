from pydicom import Dataset

from pynetdicom.sop_class import (
    DigitalXRayImageStorageForPresentation,

    PatientRootQueryRetrieveInformationModelMove,
    StudyRootQueryRetrieveInformationModelMove,
    PatientStudyOnlyQueryRetrieveInformationModelMove,
)

from . import BaseNetDicom


class DicomSCU(BaseNetDicom):
    store_contexts = [
        DigitalXRayImageStorageForPresentation
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for cx in self.store_contexts:
            self.ae.add_requested_context(cx)

    def QR_Move(self, q_level, **q_kwargs):
        if q_level == 'STUDY':
            query = StudyRootQueryRetrieveInformationModelMove
        elif q_level == 'SERIES':
            query = PatientRootQueryRetrieveInformationModelMove
        else:
            query = PatientStudyOnlyQueryRetrieveInformationModelMove

        self.ae.add_requested_context(query)

        ds = Dataset()
        ds.QueryRetrieveLevel = q_level
        for k, v in q_kwargs.items():
            setattr(ds, k, v)

        assoc = self.ae.associate(
            self.host, self.port, ae_title=self.remote_ae_title,
        )
        if assoc.is_established:
            responses = assoc.send_c_move(ds, self.ae_title, query)
            for (status, _) in responses:
                if status:
                    print('C-MOVE query status: 0x{0:04x}'.format(status.Status))
                else:
                    print(f'C-MOVE query timeout: {q_kwargs}')
                    raise Exception('DICOM C-MOVE request timed out')

            # Release the association
            assoc.release()
        else:
            raise Exception('DICOM Server [%s@%s:%s] is unavailable.'.format(
                self.remote_ae_title, self.host, self.port))