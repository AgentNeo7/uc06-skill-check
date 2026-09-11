@IsTest
private class ReviewActionTest {
    @TestSetup static void setupOperator() {
        Profile standardProfile = [SELECT Id FROM Profile WHERE Name = 'Standard User' LIMIT 1];
        User operator = new User(Alias='ucreview',Email='synthetic@example.invalid',EmailEncodingKey='UTF-8',LastName='UCReviewOperator',LanguageLocaleKey='en_US',LocaleSidKey='en_US',TimeZoneSidKey='America/Chicago',ProfileId=standardProfile.Id,Username='uc-review-'+UserInfo.getOrganizationId()+'-'+String.valueOf(DateTime.now().getTime())+'@example.invalid');
        insert operator;
        PermissionSet permission = [SELECT Id FROM PermissionSet WHERE Name='Review_Operator' LIMIT 1];
        insert new PermissionSetAssignment(AssigneeId=operator.Id,PermissionSetId=permission.Id);
    }
    @IsTest static void preservesUnrelatedFieldsAndCorrelatesBulk() {
        User operator=[SELECT Id FROM User WHERE LastName='UCReviewOperator' LIMIT 1];
        List<Review_Request__c> rows = new List<Review_Request__c>{new Review_Request__c(Name='Synthetic A',OwnerId=operator.Id,Correlation_Id__c='SYNTH-A',Status__c='Pending',Confirmed_Consent__c=true,Amount__c=10),new Review_Request__c(Name='Synthetic B',OwnerId=operator.Id,Correlation_Id__c='SYNTH-B',Status__c='Pending',Confirmed_Consent__c=true,Amount__c=20)};
        insert rows;
        ReviewAction.Request a=new ReviewAction.Request();a.correlationId='SYNTH-A';a.approve=true;
        ReviewAction.Request b=new ReviewAction.Request();b.correlationId='SYNTH-B';b.approve=false;
        List<ReviewAction.Result> result;
        System.runAs(operator) { Test.startTest();result=ReviewAction.review(new List<ReviewAction.Request>{a,b});Test.stopTest(); }
        System.assertEquals(2,result.size());System.assertEquals('Approved',result[0].status);System.assertEquals('Declined',result[1].status);
        Map<Id,Review_Request__c> actual=new Map<Id,Review_Request__c>([SELECT Status__c,Amount__c FROM Review_Request__c WHERE Id IN :rows]);
        System.assertEquals('Approved',actual.get(rows[0].Id).Status__c);System.assertEquals(10,actual.get(rows[0].Id).Amount__c);
    }
    @IsTest static void rejectsNonSyntheticIdentity() {
        ReviewAction.Request a=new ReviewAction.Request();a.correlationId='REAL';a.approve=true;
        try {ReviewAction.review(new List<ReviewAction.Request>{a});System.assert(false,'Expected refusal');} catch (IllegalArgumentException expected) {System.assert(expected.getMessage().contains('synthetic'));}
    }
    @IsTest static void refusesWithoutConsentAndPreservesState() {
        User operator=[SELECT Id FROM User WHERE LastName='UCReviewOperator' LIMIT 1];
        Review_Request__c row = new Review_Request__c(Name='No Consent',OwnerId=operator.Id,Correlation_Id__c='SYNTH-NO-CONSENT',Status__c='Pending',Amount__c=0,Confirmed_Consent__c=false);
        insert row;
        ReviewAction.Request request=new ReviewAction.Request();request.correlationId=row.Correlation_Id__c;request.approve=true;
        System.runAs(operator) {
            try { ReviewAction.review(new List<ReviewAction.Request>{request}); System.assert(false,'Expected consent refusal'); } catch (IllegalArgumentException expected) { System.assert(expected.getMessage().contains('consent')); }
        }
        System.assertEquals('Pending',[SELECT Status__c FROM Review_Request__c WHERE Id=:row.Id].Status__c);
    }
}
