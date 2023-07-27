import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { FeatureService } from './feature.service';
import { IFeature } from './feature';

@Component({
  selector: 'app-feature-selection',
  templateUrl: './feature-selection.component.html',
  styleUrls: ['./feature-selection.component.css']
})
export class FeatureSelectionComponent implements OnInit {
  checked: boolean = true;
  features: any;
  errorMsg: any;

  constructor(private featureService: FeatureService) {

  }

  onSelectAllFeatures() {
    console.log(this.features)
  }

  ngOnInit(): void {
    this.features = this.featureService.getAllFeatures()
      .subscribe({
        next: data => {
          this.features = data;
          console.log(data);
        },
        error: error => this.errorMsg = error
      })
  }

  // affectiveFeatures: Array<String> = [
  //   "Intensifier",
  //   "Hedging"
  // ];

  // nonPropositionalFeatures: Array<String> = [
  //   "Adverb for Iteration/Continuation",
  //   "Scalar Particle",
  //   "Factive Verb",
  //   "Modal Particle for Common Ground",
  //   "Modal Particle for Resigned Acceptance",
  //   "Modal Particle for Weakened Commitment"
  // ]

  // sentenceTypeFeatures: Array<String> = [
  //   "Question",
  //   "Exclamation"
  // ]

  // discourseRelationFeatures: Array<String> = [
  //   "Causal / Concessive",
  //   "Conditional",
  //   "Concessive",
  //   "Adversative"
  // ]

  
}
