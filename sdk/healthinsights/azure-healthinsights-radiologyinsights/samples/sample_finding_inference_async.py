# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import datetime
import os
import uuid


from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.radiologyinsights.aio import RadiologyInsightsClient
from azure.healthinsights.radiologyinsights import models

"""
FILE: sample_finding_inference_async.py

DESCRIPTION:
The sample_finding_inference_async.py module processes a sample radiology document with the Radiology Insights service.
It will initialize an asynchronous RadiologyInsightsClient, build a Radiology Insights request with the sample document,
submit it to the client, RadiologyInsightsClient, build a Radiology Insights job request with the sample document,
submit it to the client and display 
-the Finding resource type,
-the Finding ID,
-the Finding status,
-the Finding category code,
-the Finding code,
-the Finding interpretation,
-the Finding components,
-the Finding component code,
-the Finding component value codeable concept,
-the Finding component value coding,
-the Finding component value boolean,
-the Finding component value quantity,
-the Inference extensions,
-the Inference extension URL,
-the Inference extension value string,
-the Inference extension section
extracted by the Radiology Insights service.    


USAGE:
   
"""


class HealthInsightsSamples:
    async def radiology_insights_async(self) -> None:
        # [START create_radiology_insights_client]
        KEY = os.environ["AZURE_HEALTH_INSIGHTS_API_KEY"]
        ENDPOINT = os.environ["AZURE_HEALTH_INSIGHTS_ENDPOINT"]

        job_id = str(uuid.uuid4())

        radiology_insights_client = RadiologyInsightsClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
        # [END create_radiology_insights_client]
        doc_content1 = """FINDINGS:
        In the right upper lobe, there is a new mass measuring 5.6 x 4.5 x 3.4 cm.
        A lobulated soft tissue mass is identified in the superior right lower lobe abutting the major fissure measuring 5.4 x 4.3 x 3.7 cm (series 3 image 94, coronal image 110).
        A 4 mm nodule in the right lower lobe (series 3, image 72) is increased dating back to 6/29/2012. This may represent lower lobe metastasis.
        IMPRESSION: 4 cm pulmonary nodule posterior aspect of the right upper lobe necessitating additional imaging as described."""
        
        # Create ordered procedure
        procedure_coding = models.Coding(
            system="Https://loinc.org",
            code="24627-2",
            display="CT CHEST",
        )
        procedure_code = models.CodeableConcept(coding=[procedure_coding])
        ordered_procedure = models.OrderedProcedure(description="CT CHEST", code=procedure_code)
        # Create encounter
        start = datetime.datetime(2021, 8, 28, 0, 0, 0, 0)
        end = datetime.datetime(2021, 8, 28, 0, 0, 0, 0)
        encounter = models.PatientEncounter(
            id="encounter2",
            class_property=models.EncounterClass.IN_PATIENT,
            period=models.TimePeriod(start=start, end=end),
        )
        # Create patient info
        birth_date = datetime.date(1959, 11, 11)
        patient_info = models.PatientDetails(sex=models.PatientSex.FEMALE, birth_date=birth_date)
        # Create author
        author = models.DocumentAuthor(id="author2", full_name="authorName2")

        create_date_time = datetime.datetime(2024, 2, 19, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        patient_document1 = models.PatientDocument(
            type=models.DocumentType.NOTE,
            clinical_type=models.ClinicalDocumentType.RADIOLOGY_REPORT,
            id="doc2",
            content=models.DocumentContent(source_type=models.DocumentContentSourceType.INLINE, value=doc_content1),
            created_at=create_date_time,
            specialty_type=models.SpecialtyType.RADIOLOGY,
            administrative_metadata=models.DocumentAdministrativeMetadata(
                ordered_procedures=[ordered_procedure], encounter_id="encounter2"
            ),
            authors=[author],
            language="en",
        )

        # Construct patient
        patient1 = models.PatientRecord(
            id="patient_id2",
            details=patient_info,
            encounters=[encounter],
            patient_documents=[patient_document1],
        )

        # Create a configuration
        configuration = models.RadiologyInsightsModelConfiguration(verbose=False, include_evidence=True, locale="en-US")

        # Construct the request with the patient and configuration
        radiology_insights_data = models.RadiologyInsightsData(patients=[patient1], configuration=configuration)
        job_data = models.RadiologyInsightsJob(job_data=radiology_insights_data)

        try:
            poller = await radiology_insights_client.begin_infer_radiology_insights(
                id=job_id,
                resource=job_data,
            )
            job_response = await poller.result()
            radiology_insights_result = models.RadiologyInsightsInferenceResult(job_response)
            self.display_finding(radiology_insights_result)
            await radiology_insights_client.close()
        except Exception as ex:
            print(str(ex))
            return

    def display_finding(self, radiology_insights_result):
        # [START display_finding]
        for patient_result in radiology_insights_result.patient_results:
            counter = 0
            for ri_inference in patient_result.inferences:
                if ri_inference.kind == models.RadiologyInsightsInferenceType.FINDING:
                    counter += 1
                    print(f"Finding {counter} Inference found")
                    fin = ri_inference.finding
                    for attribute in dir(fin):
                        if attribute.startswith('_') or callable(getattr(fin, attribute)):
                            continue
                        elif attribute == "resource_type" and fin.resource_type is not None:
                            print(f"Finding {counter}: Resource Type: {fin.resource_type}")
                        elif attribute == "id" and fin.id is not None:
                            print(f"Finding {counter}: ID: {fin.id}")
                        elif attribute == "status" and fin.status is not None:
                            print(f"Finding {counter}: Status: {fin.status}")
                        elif attribute == "category" and fin.category is not None:
                            for cat in fin.category:
                                if cat.coding is not None:
                                    for code in cat.coding:
                                        if code.code is not None and code.display is not None:
                                            print(f"Finding {counter}: Category Code: {code.system} {code.code} {code.display}")
                        elif attribute == "code" and fin.code is not None:
                            for code in fin.code.coding:
                                if code.code is not None and code.display is not None:
                                    print(f"Finding {counter}: Code: {code.system} {code.code} {code.display}")
                        elif attribute == "interpretation" and fin.interpretation is not None:
                            for intpt in fin.interpretation:  
                                for code in intpt.coding:                                          
                                    if code.code is not None and code.display is not None:
                                        print(f"Finding {counter}: Interpretation: {code.system} {code.code} {code.display}")
                        elif attribute == "component" and fin.component is not None:
                            print(f"Finding {counter}: COMPONENTS:")
                            for component in fin.component:
                                for attr in dir(component):
                                    if attr.startswith('_') or callable(getattr(component, attr)):
                                        continue
                                    if attr == "code" and component.code is not None:
                                        for code in component.code.coding:
                                            if code.code is not None and code.display is not None:
                                                print(f"Finding {counter}: COMPONENTS: Code: {code.system} {code.code} {code.display}")
                                    elif attr == "value_codeable_concept" and component.value_codeable_concept is not None:
                                        for code in component.value_codeable_concept.coding:
                                            if code.code is not None and code.display is not None:
                                                print(f"Finding {counter}: COMPONENTS: Value Codeable Concept: {code.system} {code.code} {code.display}")
                                    elif attr == "value_coding" and component.value_coding is not None:
                                        for code in component.value_coding.coding:
                                            if code.code is not None and code.display is not None:
                                                print(f"Finding {counter}: COMPONENTS: Value Coding: {code.system} {code.code} {code.display}")
                                    elif attr == "value_boolean" and component.value_boolean is not None:
                                        print(f"Finding {counter}: COMPONENTS: Value Boolean: {component.value_boolean}")
                                    elif attr == "value_quantity" and component.value_quantity is not None:
                                        for attrb in dir(component.value_quantity):
                                            if not attrb.startswith('_') and not callable(getattr(component.value_quantity, attrb)) and getattr(component.value_quantity, attrb) is not None:
                                                print(f"Finding {counter}: COMPONENTS: Value Quantity: {attrb.capitalize()}: {getattr(component.value_quantity, attrb)}")       
                    inference_extension = ri_inference.extension
                    if inference_extension is not None:
                        print(f"Finding {counter}: INFERENCE EXTENSIONS:")
                        for extension in inference_extension:
                            for attr in dir(extension):
                                if attr.startswith('_') or callable(getattr(extension, attr)):
                                    continue
                                elif attr == "extension" and extension.extension is not None:
                                    for sub_extension in extension.extension:
                                        for sub_attr in dir(sub_extension):
                                            if sub_attr.startswith('_') or callable(getattr(sub_extension, sub_attr)):
                                                continue
                                            elif sub_attr == "url":
                                                if sub_extension.url == "code" or sub_extension.url == "codingSystem" or sub_extension.url == "codeSystemName" or sub_extension.url == "displayName":
                                                    print(f"Finding {counter}: INFERENCE EXTENSIONS: EXTENSION: {sub_attr.capitalize()}: {sub_extension.url}")
                                            elif sub_attr == "value_string" and sub_extension.value_string is not None:
                                                print(f"Finding {counter}: INFERENCE EXTENSIONS: EXTENSION: {sub_attr.capitalize()}: {sub_extension.value_string}")
                                elif attr == "url" and extension.url is not None:
                                    if extension.url == "section":
                                        print(f"Finding {counter}: INFERENCE EXTENSIONS: {attr.capitalize()}: {extension.url}")
                                    
        # [END display_finding]
async def main():
    sample = HealthInsightsSamples()
    await sample.radiology_insights_async()


if __name__ == "__main__":
    asyncio.run(main())