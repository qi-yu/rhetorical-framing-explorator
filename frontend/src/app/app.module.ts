import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ButtonModule } from 'primeng/button';
import { FileUploadComponent } from './file-upload/file-upload.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { StepsModule } from 'primeng/steps';
import { FileUploadModule } from 'primeng/fileupload';
import { HttpClientModule } from '@angular/common/http';
import { CardModule } from 'primeng/card';
import { PanelModule } from 'primeng/panel';
import { StepsComponent } from './steps/steps.component';
import { FeatureSelectionComponent } from './feature-selection/feature-selection.component';
import { FieldsetModule } from 'primeng/fieldset';
import { CheckboxModule } from 'primeng/checkbox';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ToggleButtonModule } from 'primeng/togglebutton';
import { FileSizePipe } from './file-upload/file-size.pipe';
import { MessagesModule } from 'primeng/messages';
import { ToastModule } from 'primeng/toast';
import { TableModule } from 'primeng/table';
import { DividerModule } from 'primeng/divider';
import { AnnotationComponent } from './annotation/annotation.component';
import { ProgressBarModule } from 'primeng/progressbar';
import { StatisticsComponent } from './statistics/statistics.component';

@NgModule({
  declarations: [
    AppComponent,
    FileUploadComponent,
    StepsComponent,
    FeatureSelectionComponent,
    FileSizePipe,
    AnnotationComponent,
    StatisticsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ButtonModule,
    BrowserAnimationsModule,
    StepsModule,
    FileUploadModule,
    HttpClientModule,
    CardModule,
    PanelModule,
    FieldsetModule,
    CheckboxModule,
    FormsModule,
    ReactiveFormsModule,
    ToggleButtonModule,
    MessagesModule,
    ToastModule,
    TableModule,
    DividerModule,
    ProgressBarModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
