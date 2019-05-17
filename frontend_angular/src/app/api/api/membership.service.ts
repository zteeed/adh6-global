/**
 * Adherent
 * Adherent api
 *
 * The version of the OpenAPI document: 1.0.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
/* tslint:disable:no-unused-variable member-ordering */

import { Inject, Injectable, Optional }                      from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams,
         HttpResponse, HttpEvent }                           from '@angular/common/http';
import { CustomHttpUrlEncodingCodec }                        from '../encoder';

import { Observable }                                        from 'rxjs';

import { MembershipRequest } from '../model/membershipRequest';

import { BASE_PATH, COLLECTION_FORMATS }                     from '../variables';
import { Configuration }                                     from '../configuration';


@Injectable({
  providedIn: 'root'
})
export class MembershipService {

    protected basePath = 'http://localhost/api';
    public defaultHeaders = new HttpHeaders();
    public configuration = new Configuration();

    constructor(protected httpClient: HttpClient, @Optional()@Inject(BASE_PATH) basePath: string, @Optional() configuration: Configuration) {

        if (configuration) {
            this.configuration = configuration;
            this.configuration.basePath = configuration.basePath || basePath || this.basePath;

        } else {
            this.configuration.basePath = basePath || this.basePath;
        }
    }

    /**
     * @param consumes string[] mime-types
     * @return true: consumes contains 'multipart/form-data', false: otherwise
     */
    private canConsumeForm(consumes: string[]): boolean {
        const form = 'multipart/form-data';
        for (const consume of consumes) {
            if (form === consume) {
                return true;
            }
        }
        return false;
    }


    /**
     * Add a membership record for an member
     * 
     * @param username The username of the member
     * @param membershipRequest Membership record, if no start is specified, it will use the current date. Duration is expressed in days. WARNING: DO NOT set the start date to be in the future, it is not implemented for the moment.
     * @param xIdempotencyKey Just a random string to ensure that membership creation is idempotent (very important since double submission may result to the member being charged two times). I recommand using a long random string for that.
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public memberUsernameMembershipPost(username: string, membershipRequest: MembershipRequest, xIdempotencyKey?: string, observe?: 'body', reportProgress?: boolean): Observable<any>;
    public memberUsernameMembershipPost(username: string, membershipRequest: MembershipRequest, xIdempotencyKey?: string, observe?: 'response', reportProgress?: boolean): Observable<HttpResponse<any>>;
    public memberUsernameMembershipPost(username: string, membershipRequest: MembershipRequest, xIdempotencyKey?: string, observe?: 'events', reportProgress?: boolean): Observable<HttpEvent<any>>;
    public memberUsernameMembershipPost(username: string, membershipRequest: MembershipRequest, xIdempotencyKey?: string, observe: any = 'body', reportProgress: boolean = false ): Observable<any> {
        if (username === null || username === undefined) {
            throw new Error('Required parameter username was null or undefined when calling memberUsernameMembershipPost.');
        }
        if (membershipRequest === null || membershipRequest === undefined) {
            throw new Error('Required parameter membershipRequest was null or undefined when calling memberUsernameMembershipPost.');
        }

        let headers = this.defaultHeaders;
        if (xIdempotencyKey !== undefined && xIdempotencyKey !== null) {
            headers = headers.set('X-Idempotency-Key', String(xIdempotencyKey));
        }

        // to determine the Accept header
        const httpHeaderAccepts: string[] = [
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected !== undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
            'application/json'
        ];
        const httpContentTypeSelected: string | undefined = this.configuration.selectHeaderContentType(consumes);
        if (httpContentTypeSelected !== undefined) {
            headers = headers.set('Content-Type', httpContentTypeSelected);
        }

        return this.httpClient.post<any>(`${this.configuration.basePath}/member/${encodeURIComponent(String(username))}/membership/`,
            membershipRequest,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

}