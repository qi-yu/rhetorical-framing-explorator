import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { IFeature } from './feature';
import { Observable, catchError, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FeatureService {
  private url: string = "/assets/data/employees.json";

  constructor(private http: HttpClient) { }

  getAllFeatures(): Observable<IFeature[]> {
    return this.http.get<IFeature[]>(this.url)
            .pipe(catchError(this.errorHandler))
  }

  errorHandler(error: HttpErrorResponse) {
    return throwError(() => (error.message || 'Server Error'));
  }

  // getFeatureByDimension(dimension: string) {
  //   return this.features
  // }
}
