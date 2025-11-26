using { BusinessPartner as BP } from '../db/schema';

service BusinessPartnerService {
    entity BusinessPartners as projection on BP;
}