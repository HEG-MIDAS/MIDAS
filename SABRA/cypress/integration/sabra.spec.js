const BaseURL = Cypress.env('base_url')
const CurrDate = new Date()
let OneYear = new Date()
OneYear.setFullYear(CurrDate.getFullYear()-1)
OneYear.setDate(CurrDate.getDate()-3)
const CurrFormatted = CurrDate.getDate()+"."+(CurrDate.getMonth()+1)+"."+CurrDate.getFullYear()
const OneYearFormatted = OneYear.getDate()+"."+(OneYear.getMonth()+1)+"."+OneYear.getFullYear()

describe('SABRA Scrapper', () => {
    it('Step', () => {
        cy.request(BaseURL)
        .should((response) => {
            if(response.status != 200){
                cy.log("Service is down !")
                throw new Error("Server is Down")
            }else{
                cy.log("Service is up !")
                cy.visit(BaseURL)
                cy.get("#submit_button").contains('Extraire')
                cy.get('table input[value="urbain"]').check()
                cy.get('table input[value="1"]').check()
                cy.get('table input[value="autre"]').check()
                cy.get('table input[name="date_from"]').type('{selectall}'+OneYearFormatted)
                cy.get('table input[name="date_to"]').type('{selectall}'+CurrFormatted)
                cy.get('table input[value="quot"]').check()
                cy.get('#submit_button').click()
                cy.get('a["title="Télécharger les données"]').click()
            }
        })
    })
})
