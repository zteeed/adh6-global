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

import { Switch } from '../model/switch';

import { BASE_PATH, COLLECTION_FORMATS }                     from '../variables';
import { Configuration }                                     from '../configuration';


@Injectable({
  providedIn: 'root'
})
export class SwitchService {

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
     * Get all switches
     * 
     * @param limit Limit the number of switches returned in the result. Default is 100
     * @param offset Skip the first n results
     * @param terms Search terms
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public switchGet(limit?: number, offset?: number, terms?: string, observe?: 'body', reportProgress?: boolean): Observable<Array<Switch>>;
    public switchGet(limit?: number, offset?: number, terms?: string, observe?: 'response', reportProgress?: boolean): Observable<HttpResponse<Array<Switch>>>;
    public switchGet(limit?: number, offset?: number, terms?: string, observe?: 'events', reportProgress?: boolean): Observable<HttpEvent<Array<Switch>>>;
    public switchGet(limit?: number, offset?: number, terms?: string, observe: any = 'body', reportProgress: boolean = false ): Observable<any> {

        let queryParameters = new HttpParams({encoder: new CustomHttpUrlEncodingCodec()});
        if (limit !== undefined && limit !== null) {
            queryParameters = queryParameters.set('limit', <any>limit);
        }
        if (offset !== undefined && offset !== null) {
            queryParameters = queryParameters.set('offset', <any>offset);
        }
        if (terms !== undefined && terms !== null) {
            queryParameters = queryParameters.set('terms', <any>terms);
        }

        let headers = this.defaultHeaders;

        // to determine the Accept header
        const httpHeaderAccepts: string[] = [
            'application/json'
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected !== undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
        ];

        return this.httpClient.get<Array<Switch>>(`${this.configuration.basePath}/switch/`,
            {
                params: queryParameters,
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Create a switch
     * 
     * @param _switch Switch to create
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public switchPost(_switch: Switch, observe?: 'body', reportProgress?: boolean): Observable<any>;
    public switchPost(_switch: Switch, observe?: 'response', reportProgress?: boolean): Observable<HttpResponse<any>>;
    public switchPost(_switch: Switch, observe?: 'events', reportProgress?: boolean): Observable<HttpEvent<any>>;
    public switchPost(_switch: Switch, observe: any = 'body', reportProgress: boolean = false ): Observable<any> {
        if (_switch === null || _switch === undefined) {
            throw new Error('Required parameter _switch was null or undefined when calling switchPost.');
        }

        let headers = this.defaultHeaders;

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

        return this.httpClient.post<any>(`${this.configuration.basePath}/switch/`,
            _switch,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Delete a switch
     * 
     * @param switchID 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public switchSwitchIDDelete(switchID: number, observe?: 'body', reportProgress?: boolean): Observable<any>;
    public switchSwitchIDDelete(switchID: number, observe?: 'response', reportProgress?: boolean): Observable<HttpResponse<any>>;
    public switchSwitchIDDelete(switchID: number, observe?: 'events', reportProgress?: boolean): Observable<HttpEvent<any>>;
    public switchSwitchIDDelete(switchID: number, observe: any = 'body', reportProgress: boolean = false ): Observable<any> {
        if (switchID === null || switchID === undefined) {
            throw new Error('Required parameter switchID was null or undefined when calling switchSwitchIDDelete.');
        }

        let headers = this.defaultHeaders;

        // to determine the Accept header
        const httpHeaderAccepts: string[] = [
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected !== undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
        ];

        return this.httpClient.delete<any>(`${this.configuration.basePath}/switch/${encodeURIComponent(String(switchID))}`,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Retrieve a switch
     * 
     * @param switchID 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public switchSwitchIDGet(switchID: number, observe?: 'body', reportProgress?: boolean): Observable<Switch>;
    public switchSwitchIDGet(switchID: number, observe?: 'response', reportProgress?: boolean): Observable<HttpResponse<Switch>>;
    public switchSwitchIDGet(switchID: number, observe?: 'events', reportProgress?: boolean): Observable<HttpEvent<Switch>>;
    public switchSwitchIDGet(switchID: number, observe: any = 'body', reportProgress: boolean = false ): Observable<any> {
        if (switchID === null || switchID === undefined) {
            throw new Error('Required parameter switchID was null or undefined when calling switchSwitchIDGet.');
        }

        let headers = this.defaultHeaders;

        // to determine the Accept header
        const httpHeaderAccepts: string[] = [
            'application/json'
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected !== undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
        ];

        return this.httpClient.get<Switch>(`${this.configuration.basePath}/switch/${encodeURIComponent(String(switchID))}`,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Update a switch
     * 
     * @param switchID 
     * @param _switch Switch to update
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public switchSwitchIDPut(switchID: number, _switch: Switch, observe?: 'body', reportProgress?: boolean): Observable<any>;
    public switchSwitchIDPut(switchID: number, _switch: Switch, observe?: 'response', reportProgress?: boolean): Observable<HttpResponse<any>>;
    public switchSwitchIDPut(switchID: number, _switch: Switch, observe?: 'events', reportProgress?: boolean): Observable<HttpEvent<any>>;
    public switchSwitchIDPut(switchID: number, _switch: Switch, observe: any = 'body', reportProgress: boolean = false ): Observable<any> {
        if (switchID === null || switchID === undefined) {
            throw new Error('Required parameter switchID was null or undefined when calling switchSwitchIDPut.');
        }
        if (_switch === null || _switch === undefined) {
            throw new Error('Required parameter _switch was null or undefined when calling switchSwitchIDPut.');
        }

        let headers = this.defaultHeaders;

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

        return this.httpClient.put<any>(`${this.configuration.basePath}/switch/${encodeURIComponent(String(switchID))}`,
            _switch,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

}
