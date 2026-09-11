public with sharing class ReviewAction {
    public class Request {
        @InvocableVariable(required=true)
        public String correlationId;
        @InvocableVariable(required=true)
        public Boolean approve;
    }
    public class Result {
        @InvocableVariable
        public String status;
    }
    @InvocableMethod(label='Review Synthetic Request' description='Updates only synthetic test-owned servicing requests.')
    public static List<Result> review(List<Request> requests) {
        if (requests == null) { throw new IllegalArgumentException('Requests are required'); }
        Set<String> keys = new Set<String>();
        for (Request r : requests) {
            if (r == null || String.isBlank(r.correlationId) || r.approve == null || !r.correlationId.startsWith('SYNTH-')) {
                throw new IllegalArgumentException('A synthetic correlation ID and decision are required');
            }
            if (!keys.add(r.correlationId)) { throw new IllegalArgumentException('Duplicate correlation ID'); }
        }
        Map<String, Review_Request__c> byKey = new Map<String, Review_Request__c>();
        List<Review_Request__c> ownedRows = [SELECT Id, Correlation_Id__c, Status__c, Confirmed_Consent__c FROM Review_Request__c WHERE Correlation_Id__c IN :keys WITH USER_MODE];
        for (Review_Request__c row : ownedRows) { byKey.put(row.Correlation_Id__c, row); }
        List<Review_Request__c> updates = new List<Review_Request__c>();
        List<Result> results = new List<Result>();
        for (Request r : requests) {
            if (!byKey.containsKey(r.correlationId)) { throw new IllegalArgumentException('Owned request missing'); }
            Review_Request__c row = byKey.get(r.correlationId);
            if (!row.Confirmed_Consent__c) { throw new IllegalArgumentException('Confirmed consent is required'); }
            row.Status__c = r.approve ? 'Approved' : 'Declined';
            updates.add(new Review_Request__c(Id=row.Id,Status__c=row.Status__c));
            Result outcome = new Result(); outcome.status = row.Status__c; results.add(outcome);
        }
        update as user updates;
        return results;
    }
}
