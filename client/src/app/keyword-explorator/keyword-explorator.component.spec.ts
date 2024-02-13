import { ComponentFixture, TestBed } from '@angular/core/testing';

import { KeywordExploratorComponent } from './keyword-explorator.component';

describe('KeywordExploratorComponent', () => {
  let component: KeywordExploratorComponent;
  let fixture: ComponentFixture<KeywordExploratorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ KeywordExploratorComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(KeywordExploratorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
