import { HttpClient } from '@angular/common/http';
import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { API_URL } from '../env';
import { IFile } from './file';
import { MessageService, Message } from 'primeng/api';
import { FileService } from './file.service';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css'],
  providers: [MessageService]
})


export class FileUploadComponent implements OnInit {
  @Output() fileSelectionEvent: EventEmitter<boolean> = new EventEmitter();

  url = `${API_URL}`;
  isFileDragOver: boolean = false;
  uploadedFiles: IFile[] = [];
  filesSelectedForAnalyses: IFile[] = [];
  formData: FormData = new FormData();

  constructor(
    private http: HttpClient, 
    private messageService: MessageService, 
    private fileService: FileService) {}


  onDragEnter(event: Event) {
    event.preventDefault();
    this.isFileDragOver = true;
  }

  onDragLeave(event: Event) {
    event.preventDefault();
    this.isFileDragOver = false;
  }
  
  onUploadFile(event: any): void {
    this.http.post<IFile>(`${this.url}/upload`, event.files).subscribe({
      next: () => {
        this.fileService.getAllFiles().subscribe((data) => {
          this.uploadedFiles = data;
          this.filesSelectedForAnalyses = data;
        });

        this.messageService.add({severity: 'success', summary: 'Success', detail: 'File(s) uploaded successfully!'});
      },

      error: () => {
        this.messageService.add({severity: 'error', summary: 'Error', detail: 'File(s) cannot be uploaded successfully!'});
      }
    });
  }

  onDeleteUploadedFile(file: IFile): void {
    this.fileService.deleteFile(file.filename).subscribe({
      next: () => {
        this.uploadedFiles = this.uploadedFiles.filter((uploadedFile) => uploadedFile.filename !== file.filename);
        this.filesSelectedForAnalyses = this.filesSelectedForAnalyses.filter((selectedFile) => selectedFile.filename !== file.filename);
        this.messageService.add({severity: 'success', summary: 'Success', detail: 'File(s) deleted successfully!'});
      }, 
      error: () => {
        this.messageService.add({severity: 'error', summary: 'Error', detail: 'File(s) cannot be deleted successfully!'});
      }
    });
  }

  onChangeSelectionStatus(fileToChange: IFile): void {
    this.filesSelectedForAnalyses = this.filesSelectedForAnalyses.filter((file) => file.selectedForAnalyses === true);
  }

  onFileSelection(): void {
   this.filesSelectedForAnalyses.length > 0
    ? this.fileSelectionEvent.emit(true)
    : this.fileSelectionEvent.emit(false);
  }

  ngOnInit(): void {
    this.fileService.getAllFiles()
      .subscribe((data) => {
        this.uploadedFiles = data;
        this.filesSelectedForAnalyses = data;
        this.onFileSelection();
      })
  }
}
