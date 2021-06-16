mkdir ../dataset/
mkdir ../dataset/dumps_dataset
mkdir ../dataset/extracted_dataset
mkdir ../dataset/indexing_dataset
mkdir ../dataset/indexing_dataset/inverted_index
mkdir ../dataset/indexing_dataset/positional_index
mkdir ../dataset/indexing_dataset/document_vector_index

cd ../dataset/dumps_dataset


#for debug
wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles11.xml-p6899367p7054859.bz2
bzip2 -d enwiki-latest-pages-articles11.xml-p6899367p7054859.bz2
python ../../preprocessing/WikiExtractor.py -b8M --json enwiki-latest-pages-articles11.xml-p6899367p7054859
mv */ ../extracted_dataset/

#for full dataset
#wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2
#bzip2 -d enwiki-latest-pages-articles.xml.bz2
#python ../../preprocessing/WikiExtractor.py -b8M --json enwiki-latest-pages-articles.xml
#mv */ ../extracted_dataset/
