import os
import langchain
from textwrap import dedent


from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains.question_answering import load_qa_chain
import pinecone
from langchain_openai import OpenAIEmbeddings


import openai




from dotenv import load_dotenv
load_dotenv()


# Set API keys
os.environ['OPENAI_API_KEY'] =  os.getenv("OPENAI_API_KEY")

os.environ['PINECONE_API_KEY'] = os.getenv("PINECONE_API_KEY")

#pinecone.init(api_key=os.environ['PINECONE_API_KEY'], environment="us-east-1")

# Initialize embeddings and vector store
index_name = "branding-course"
embedding = OpenAIEmbeddings()
#index = pinecone.Index(index_name=index_name, api_key=os.environ['PINECONE_API_KEY'])
vector_store = PineconeVectorStore(index_name=index_name, embedding=embedding, namespace= "brandingcourse")


memory = ConversationBufferWindowMemory(memory_key="chat_history", input_key="question", human_prefix= "User", ai_prefix= "Assistant")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

class RAGbot:
      
    
    def run(prompt): #need to pass user query and memory variable.
       
        #try:  
               
          
      
            prompt_template =dedent(r"""
              

            You are an expert in branding, and you have access to a full course on branding strategies, techniques, and best practices. I will ask you two questions about my company's branding, and I need you to provide a detailed and actionable response using the information from the course. Please ensure your response covers key branding elements such as brand identity, positioning, messaging, tone of voice, visual elements, and customer engagement strategies.

            
             
            Explain how I can establish a strong brand identity that aligns with my company's values, mission, and target audience.  
            Provide detailed steps on how to create a memorable brand image and position it in the market based on the course materials.

 
            Provide guidance on developing a brand story and key messages that communicate the essence of my brand and connect with customers emotionally.  
            Include suggestions on how to maintain brand consistency across different channels and touchpoints.

            Please ensure your answer references different sections from the branding course to cover all relevant aspects, including practical examples and advice on how to implement the strategies effectively.

            


              This is the context from branding course:
              ---------
              {context}

              Questions: 
              {question}

              Helpful Answer: 
              """)
              
              

            PROMPT = PromptTemplate(
                    template=prompt_template, input_variables=[ "context", "question"]
                )

                
            chain = load_qa_chain(llm=llm, verbose= True, prompt = PROMPT, chain_type="stuff")
                    
        
        
         
            
            docs =vector_store.similarity_search(prompt, namespace="brandingcourse")
            
            
            response = chain.run(input_documents=docs, question=prompt)
            
            
            memory.save_context({"question": prompt}, {"output": response})
            
            
                
            return response
            
        #except Exception as e:
            
         #   "Sorry, the question is irrelevant or the bot crashed"
    


if __name__ == "__main__":
      print("## Welcome to the RAG chatbot")
      print('-------------------------------')
      
      while True:
        query = input("You: ")
        if query.lower() == 'exit':
            break
        chatbot= RAGbot
        result = chatbot.run(query)
        print("Bot:", result)