import { HttpClient } from '@angular/common/http';
import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { API_URL } from '../env';
import { IFile } from './file';
import { MessageService, Message } from 'primeng/api';
import { FileService } from './file.service';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css'],
  providers: [MessageService]
})


export class FileUploadComponent implements OnInit {
  @Output() uploadCompletedEvent = new EventEmitter<boolean>();

  url = `${API_URL}`;
  isFileDragOver: boolean = false;
  uploadedFiles: IFile[] = [];
  formData: FormData = new FormData();
  filesSelectedForAnalyses: IFile[] = [];
  uploadCompleted = false;
  uploadSuccessMessage: Message[] = [ {severity: 'success', summary: 'Success', detail: 'File uploaded successfully!'} ]
  uploadErrorMessage: Message[] = [ {severity: 'error', summary: 'Error', detail: 'File cannot be uploaded successfully!'} ]

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
        this.uploadCompleted = true;
        this.uploadCompletedEvent.emit(this.uploadCompleted);
        this.showSuccessMessage();

        // Fetch the updated list of uploaded files
        this.fileService.getAllFiles().subscribe((data) => {
          this.uploadedFiles = data;
          this.filesSelectedForAnalyses = data;
        });
      },

      error: () => {
        this.uploadCompleted = false; 
        this.uploadCompletedEvent.emit(this.uploadCompleted);
        this.showErrorMessage();
      }
    });
  }

  onDeleteUploadedFile(file: IFile): void {
    this.fileService.deleteFile(file.filename).subscribe({
      next: () => {
        this.uploadedFiles = this.uploadedFiles.filter((uploadedFile) => uploadedFile.filename !== file.filename);
        console.log('File deleted successfully!');
      }, 
      error: () => {
        console.log('Failed to delete the file.');
      }
    });
  }

  onToggleFileForAnalyses(file: IFile): void {
    for(let i = 0; i < this.filesSelectedForAnalyses.length - 1; i++) {
      if(this.filesSelectedForAnalyses[i].filename === file.filename) {
        this.filesSelectedForAnalyses[i].selectedForAnalyses = !this.filesSelectedForAnalyses[i].selectedForAnalyses
      }
    }
    
    this.filesSelectedForAnalyses = this.filesSelectedForAnalyses.filter((file) => file.selectedForAnalyses === true);
    console.log(this.filesSelectedForAnalyses)
  }

  showSuccessMessage(): void {
    this.messageService.addAll(this.uploadSuccessMessage);
  }

  showErrorMessage(): void {
    this.messageService.addAll(this.uploadErrorMessage);
  }

  ngOnInit(): void {
    this.fileService.getAllFiles()
      .subscribe((data) => {
        this.uploadedFiles = data;
        this.filesSelectedForAnalyses = data;
      })
  }

}
